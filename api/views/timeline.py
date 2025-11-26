from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from follow.models import Follow
from post.models import Like, Post

from ..serializers import PostSerializer


class TimelinePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class TimelineView(ListAPIView):
    """Provide latest/popular/following timeline feeds."""

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = TimelinePagination
    _page_post_ids = None

    def get_queryset(self):
        tab = self.request.query_params.get("tab", "latest")
        base_qs = Post.objects.select_related("user")
        if tab == "popular":
            window = timezone.now() - timedelta(hours=24)
            return base_qs.filter(time__gte=window).order_by("-like_count", "-time")
        if tab == "following":
            user = self.request.user
            if not user.is_authenticated:
                return Post.objects.none()
            following_ids = Follow.objects.filter(user=user).values_list("aim_user_id", flat=True)
            return base_qs.filter(user_id__in=following_ids).order_by("-time")
        # default latest
        return base_qs.order_by("-time")

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
