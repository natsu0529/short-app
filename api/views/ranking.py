from datetime import timedelta

from django.db.models import F, Window
from django.db.models.functions import Rank
from django.utils import timezone
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination, PageNumberPagination

from accounts.models import CustomUser
from post.models import Like, Post

from ..serializers import CustomUserSerializer, PostSerializer


class RankingCursorPagination(CursorPagination):
    """Cursor-based pagination for post rankings."""

    page_size = 20
    ordering = ("-like_count", "-post_id")
    cursor_query_param = "cursor"


class UserRankingPagination(PageNumberPagination):
    """Page-based pagination for user rankings (Window関数との互換性のため)."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class PostLikeRankingView(ListAPIView):
    """Top posts by like_count. Optional ?range=24h"""

    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = RankingCursorPagination
    _page_post_ids = None

    def get_queryset(self):
        qs = Post.objects.select_related("user")
        range_param = (self.request.query_params.get("range") or "").lower()
        if range_param == "24h":
            window = timezone.now() - timedelta(hours=24)
            qs = qs.filter(time__gte=window)
        return qs.order_by("-like_count", "-post_id")

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        if page is not None:
            self._page_post_ids = [post.post_id for post in page]
        return page

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if getattr(user, "is_authenticated", False) and self._page_post_ids:
            liked_ids = set(
                Like.objects.filter(user=user, post_id__in=self._page_post_ids).values_list(
                    "post_id", flat=True
                )
            )
            context["liked_post_ids"] = liked_ids
        return context


class UserTotalLikesRankingView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = UserRankingPagination

    def get_queryset(self):
        return (
            CustomUser.objects.select_related("stats")
            .annotate(
                like_rank=Window(
                    expression=Rank(),
                    order_by=[
                        F("stats__total_likes_received").desc(),
                        F("date_joined").asc(),
                    ],
                )
            )
            .order_by("-stats__total_likes_received", "-date_joined")
        )


class UserLevelRankingView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = UserRankingPagination

    def get_queryset(self):
        return CustomUser.objects.select_related("stats").order_by(
            "-user_level", "-date_joined"
        )


class UserFollowerRankingView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = UserRankingPagination

    def get_queryset(self):
        return (
            CustomUser.objects.select_related("stats")
            .order_by("-stats__follower_count", "-date_joined")
        )
