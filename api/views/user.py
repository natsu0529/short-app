from django.db.models import F, Window
from django.db.models.functions import DenseRank
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from accounts.models import CustomUser

from ..serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        base_qs = CustomUser.objects.select_related("stats")
        return base_qs.annotate(
            like_rank=Window(
                expression=DenseRank(),
                order_by=[
                    F("stats__total_likes_received").desc(nulls_last=True),
                ],
            )
        ).order_by("-stats__total_likes_received", "-date_joined")

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [permissions.AllowAny]
        elif self.action == "me":
            permission_classes = [permissions.IsAuthenticated]
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

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
