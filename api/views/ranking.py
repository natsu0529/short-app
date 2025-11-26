from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from accounts.models import CustomUser
from post.models import Post

from ..serializers import CustomUserSerializer, PostSerializer


class RankingPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class PostLikeRankingView(ListAPIView):
    """Top posts by like_count. Optional ?range=24h"""

    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = RankingPagination

    def get_queryset(self):
        qs = Post.objects.select_related("user")
        range_param = (self.request.query_params.get("range") or "").lower()
        if range_param == "24h":
            window = timezone.now() - timedelta(hours=24)
            qs = qs.filter(time__gte=window)
        return qs.order_by("-like_count", "-time")


class UserTotalLikesRankingView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = RankingPagination

    def get_queryset(self):
        return (
            CustomUser.objects.select_related("stats")
            .order_by("-stats__total_likes_received", "-date_joined")
        )


class UserLevelRankingView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = RankingPagination

    def get_queryset(self):
        return CustomUser.objects.select_related("stats").order_by(
            "-user_level", "-date_joined"
        )


class UserFollowerRankingView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = RankingPagination

    def get_queryset(self):
        return (
            CustomUser.objects.select_related("stats")
            .order_by("-stats__follower_count", "-date_joined")
        )
