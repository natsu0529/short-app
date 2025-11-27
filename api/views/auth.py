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
