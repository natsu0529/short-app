from django.db import transaction
from django.db.models import F
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from post.models import Like, Post

from ..serializers import LikeSerializer, PostSerializer


class LikeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Like.objects.select_related("user", "post", "post__user")
        user_id = self.request.query_params.get("user_id")
        post_id = self.request.query_params.get("post_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("ログインしてください。")
        with transaction.atomic():
            like = serializer.save(user=self.request.user)
            Post.objects.filter(pk=like.post_id).update(like_count=F("like_count") + 1)
            author_stats = getattr(like.post.user, "stats", None)
            if author_stats:
                author_stats.register_like_received(value=1)
            liker_stats = getattr(self.request.user, "stats", None)
            if liker_stats:
                liker_stats.register_like_given(value=1)

        # Send push notification (outside transaction)
        post_author = like.post.user
        if post_author.user_id != self.request.user.user_id:
            from ..services.notifications import (
                check_and_notify_post_ranking,
                check_and_notify_user_likes_ranking,
                notify_liked,
            )

            notify_liked(
                post_author_id=post_author.user_id,
                liker_username=self.request.user.username,
                post_context=like.post.context or "",
            )
            # Check ranking notifications
            check_and_notify_post_ranking(like.post.post_id, post_author.user_id)
            check_and_notify_user_likes_ranking(post_author.user_id)

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.user != user and not user.is_staff:
            raise PermissionDenied("自分のいいねのみ解除できます。")
        with transaction.atomic():
            post = instance.post
            instance.delete()
            Post.objects.filter(pk=post.pk, like_count__gt=0).update(
                like_count=F("like_count") - 1
            )
            author_stats = getattr(post.user, "stats", None)
            if author_stats and author_stats.total_likes_received > 0:
                author_stats.total_likes_received -= 1
                author_stats.save(update_fields=["total_likes_received"])
            liker_stats = getattr(user, "stats", None)
            if liker_stats and liker_stats.total_likes_given > 0:
                liker_stats.total_likes_given -= 1
                liker_stats.save(update_fields=["total_likes_given"])


class LikedPostsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LikedPostsView(ListAPIView):
    """List posts liked by a specific user."""

    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LikedPostsPagination
    _page_post_ids = None

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return (
            Post.objects.select_related("user")
            .filter(likes__user_id=user_id)
            .order_by("-likes__created_at", "-time")
        )

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


class PostLikedStatusView(APIView):
    """Return liked post ids for the authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ids_param = (request.query_params.get("ids") or "").strip()
        if not ids_param:
            return Response({"liked_post_ids": []})
        try:
            post_ids = [int(pid) for pid in ids_param.split(",") if pid]
        except ValueError:
            raise ValidationError("無効な投稿IDが含まれています。")
        liked = (
            Like.objects.filter(user=request.user, post_id__in=post_ids)
            .values_list("post_id", flat=True)
        )
        return Response({"liked_post_ids": sorted(set(liked))})
