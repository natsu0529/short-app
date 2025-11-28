from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import DeviceToken


class DeviceTokenView(APIView):
    """
    POST: Register or update device token
    DELETE: Remove device token
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Register or update FCM device token."""
        token = request.data.get("token")
        platform = request.data.get("platform")

        if not token:
            return Response(
                {"error": "token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if platform not in [DeviceToken.PLATFORM_IOS, DeviceToken.PLATFORM_ANDROID]:
            return Response(
                {"error": "platform must be 'ios' or 'android'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update existing or create new
        device_token, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                "user": request.user,
                "platform": platform,
                "is_active": True,
            },
        )

        return Response(
            {
                "message": "Token registered" if created else "Token updated",
                "token_id": device_token.id,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request):
        """Remove device token (logout or unregister)."""
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = DeviceToken.objects.filter(
            user=request.user,
            token=token,
        ).delete()

        if deleted_count == 0:
            return Response(
                {"error": "Token not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "Token removed"},
            status=status.HTTP_200_OK,
        )
