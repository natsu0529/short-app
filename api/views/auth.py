import json

import jwt
import requests as http_requests
from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser


class GoogleAuthView(APIView):
    """Google ID Tokenを検証してAPIトークンを発行するビュー"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        email = request.data.get("email")
        display_name = request.data.get("display_name")

        if not token:
            return Response(
                {"error": "id_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Google ID Token 検証（iOS/Android 両方の Client ID で試行）
        idinfo = None
        last_error = None
        for client_id in settings.GOOGLE_CLIENT_IDS:
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    client_id,
                )
                break  # 検証成功
            except ValueError as e:
                last_error = e
                continue

        if idinfo is None:
            return Response(
                {"error": f"Invalid token: {str(last_error)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # トークンからemailを取得（リクエストのemailより優先）
        verified_email = idinfo.get("email", email)
        if not verified_email:
            return Response(
                {"error": "Email not found in token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ユーザー取得または作成
        user, created = CustomUser.objects.get_or_create(
            user_mail=verified_email,
            defaults={
                "username": verified_email,
                "user_name": display_name or idinfo.get("name") or verified_email.split("@")[0],
            },
        )

        # トークン発行
        api_token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": api_token.key})


class AppleAuthView(APIView):
    """Apple ID Tokenを検証してAPIトークンを発行するビュー"""

    permission_classes = [permissions.AllowAny]

    def _verify_apple_token(self, identity_token: str) -> dict:
        """
        Appleから発行されたIdentity Tokenを検証

        Args:
            identity_token: Apple Identity Token (JWT)

        Returns:
            デコードされたトークン情報

        Raises:
            ValueError: トークンの検証に失敗した場合
        """
        # Appleの公開鍵を取得
        apple_public_keys_url = "https://appleid.apple.com/auth/keys"
        try:
            response = http_requests.get(apple_public_keys_url, timeout=10)
            response.raise_for_status()
            apple_public_keys = response.json()
        except Exception as e:
            raise ValueError(f"Failed to fetch Apple public keys: {e}")

        # JWTヘッダーからkidを取得
        try:
            headers = jwt.get_unverified_header(identity_token)
            kid = headers.get("kid")
            if not kid:
                raise ValueError("No kid found in token header")
        except Exception as e:
            raise ValueError(f"Failed to decode token header: {e}")

        # 対応する公開鍵を探す
        public_key = None
        for key in apple_public_keys.get("keys", []):
            if key.get("kid") == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                break

        if not public_key:
            raise ValueError("Public key not found for the given kid")

        # トークンを検証（複数のClient IDで試行）
        decoded = None
        last_error = None
        for client_id in settings.APPLE_CLIENT_IDS:
            try:
                decoded = jwt.decode(
                    identity_token,
                    public_key,
                    algorithms=["RS256"],
                    audience=client_id,
                    issuer="https://appleid.apple.com",
                )
                break  # 検証成功
            except jwt.InvalidTokenError as e:
                last_error = e
                continue

        if decoded is None:
            raise ValueError(f"Invalid token: {str(last_error)}")

        return decoded

    def post(self, request):
        identity_token = request.data.get("identity_token")
        user_id = request.data.get("user_id")
        email = request.data.get("email")
        given_name = request.data.get("given_name")
        family_name = request.data.get("family_name")

        if not identity_token or not user_id:
            return Response(
                {"error": "identity_token and user_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Identity Tokenを検証
        try:
            decoded_token = self._verify_apple_token(identity_token)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # decoded_tokenから情報を取得
        apple_user_id = decoded_token.get("sub")
        if apple_user_id != user_id:
            return Response(
                {"error": "user_id mismatch"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ユーザーをDBで検索（apple_user_idで）
        try:
            user = CustomUser.objects.get(apple_user_id=apple_user_id)
        except CustomUser.DoesNotExist:
            # 新規ユーザーの場合は作成
            # 注意：email, given_name, family_nameは初回ログインのみ提供される
            display_name = f"{given_name or ''} {family_name or ''}".strip() or "Apple User"

            # メールアドレスの処理
            if email:
                user_email = email
            else:
                # メールがない場合のフォールバック
                user_email = f"{apple_user_id}@apple.privaterelay.com"

            # ユニークなusernameを生成
            base_username = f"apple_{apple_user_id[:8]}"
            username = base_username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = CustomUser.objects.create(
                apple_user_id=apple_user_id,
                user_mail=user_email,
                user_name=display_name,
                username=username,
            )

        # トークン発行
        api_token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": api_token.key})
