from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from follow.models import Follow

from ..serializers import FollowSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Follow.objects.select_related("user", "aim_user").all()
        user_id = self.request.query_params.get("user_id")
        aim_user_id = self.request.query_params.get("aim_user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if aim_user_id:
            queryset = queryset.filter(aim_user_id=aim_user_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("自分のフォローのみ解除できます。")
        instance.delete()
