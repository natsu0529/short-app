from datetime import timedelta

from django.db.models import Subquery
from django.utils import timezone
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination

from follow.models import Follow
from post.models import Like, Post

from ..serializers import PostSerializer


class TimelineCursorPagination(CursorPagination):
    """Cursor-based pagination for efficient deep page access."""

    page_size = 20
    ordering = "-post_id"  # 一意のフィールドでソート（timeより高速）
    cursor_query_param = "cursor"


class PopularCursorPagination(CursorPagination):
    """Cursor pagination for popular tab (like_count, then post_id)."""

    page_size = 20
    ordering = ("-like_count", "-post_id")
    cursor_query_param = "cursor"


class TimelineView(ListAPIView):
    """Provide latest/popular/following timeline feeds."""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    _page_post_ids = None

    def get_pagination_class(self):
        tab = self.request.query_params.get("tab", "latest")
        if tab == "popular":
            return PopularCursorPagination
        return TimelineCursorPagination

    @property
    def pagination_class(self):
        return self.get_pagination_class()

    def get_queryset(self):
        tab = self.request.query_params.get("tab", "latest")
        base_qs = Post.objects.select_related("user")
        if tab == "popular":
            window = timezone.now() - timedelta(hours=24)
            return base_qs.filter(time__gte=window).order_by("-like_count", "-post_id")
        if tab == "following":
            user = self.request.user
            if not user.is_authenticated:
                return Post.objects.none()
            # サブクエリを使用してDB内で処理（メモリ効率向上）
            following_subquery = Follow.objects.filter(user=user).values("aim_user_id")
            return base_qs.filter(user_id__in=Subquery(following_subquery)).order_by("-post_id")
        # default latest
        return base_qs.order_by("-post_id")

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
