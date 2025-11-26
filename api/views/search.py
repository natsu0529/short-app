from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from accounts.models import CustomUser
from post.models import Post

from ..serializers import CustomUserSerializer, PostSerializer


class SearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserSearchView(ListAPIView):
    serializer_class = CustomUserSerializer
    pagination_class = SearchPagination

    def get_queryset(self):
        query = (self.request.query_params.get("q") or "").strip()
        if not query:
            return CustomUser.objects.none()
        return (
            CustomUser.objects.select_related("stats")
            .filter(Q(username__icontains=query) | Q(user_name__icontains=query))
            .order_by("-stats__total_likes_received", "-user_level", "-date_joined")
        )


class PostSearchView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = SearchPagination

    def get_queryset(self):
        query = (self.request.query_params.get("q") or "").strip()
        if not query:
            return Post.objects.none()
        return (
            Post.objects.select_related("user")
            .filter(context__icontains=query)
            .order_by("-like_count", "-time")
        )
