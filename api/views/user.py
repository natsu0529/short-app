from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import CustomUser

from ..serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by("-date_joined")
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user != instance and not user.is_staff:
            raise PermissionDenied("自分のアカウントのみ更新できます。")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user != instance and not user.is_staff:
            raise PermissionDenied("自分のアカウントのみ削除できます。")
        instance.delete()
