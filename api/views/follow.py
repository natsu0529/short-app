from django.db.models import F
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from follow.models import Follow

from ..serializers import FollowSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Follow.objects.select_related("user", "aim_user").all()
        # 自分自身をフォローしているレコードを除外
        queryset = queryset.exclude(user_id=F("aim_user_id"))
        user_id = self.request.query_params.get("user_id")
        aim_user_id = self.request.query_params.get("aim_user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if aim_user_id:
            queryset = queryset.filter(aim_user_id=aim_user_id)
        return queryset

    def perform_create(self, serializer):
        follow = serializer.save(user=self.request.user)
        follower_stats = getattr(self.request.user, "stats", None)
        target_stats = getattr(follow.aim_user, "stats", None)
        if follower_stats:
            follower_stats.update_follow_counts(following_delta=1)
        if target_stats:
            target_stats.update_follow_counts(followers_delta=1)

        # Send push notification
        from ..services.notifications import (
            check_and_notify_user_follower_ranking,
            notify_followed,
        )

        notify_followed(
            target_user_id=follow.aim_user.user_id,
            follower_username=self.request.user.username,
        )
        # Check follower ranking notification
        check_and_notify_user_follower_ranking(follow.aim_user.user_id)

    def perform_destroy(self, instance):
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("自分のフォローのみ解除できます。")
        follower_stats = getattr(instance.user, "stats", None)
        target_stats = getattr(instance.aim_user, "stats", None)
        instance.delete()
        if follower_stats:
            follower_stats.update_follow_counts(following_delta=-1)
        if target_stats:
            target_stats.update_follow_counts(followers_delta=-1)
