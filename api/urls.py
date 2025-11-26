from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    FollowViewSet,
    PostSearchView,
    PostViewSet,
    TimelineView,
    UserSearchView,
)

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="user")
router.register("posts", PostViewSet, basename="post")
router.register("follows", FollowViewSet, basename="follow")

urlpatterns = [
    path("", include(router.urls)),
    path("timeline/", TimelineView.as_view(), name="timeline"),
    path("search/users/", UserSearchView.as_view(), name="search-users"),
    path("search/posts/", PostSearchView.as_view(), name="search-posts"),
]
