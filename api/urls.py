from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    DeviceTokenView,
    FollowViewSet,
    LikeViewSet,
    LikedPostsView,
    PostLikeRankingView,
    PostLikedStatusView,
    PostSearchView,
    PostViewSet,
    TimelineView,
    UserFollowerRankingView,
    UserLevelRankingView,
    UserSearchView,
    UserTotalLikesRankingView,
)
from .views.auth import GoogleAuthView

router = DefaultRouter()
router.register("users", CustomUserViewSet, basename="user")
router.register("posts", PostViewSet, basename="post")
router.register("follows", FollowViewSet, basename="follow")
router.register("likes", LikeViewSet, basename="like")

urlpatterns = [
    path("auth/google/", GoogleAuthView.as_view(), name="google-auth"),
    path("device-token/", DeviceTokenView.as_view(), name="device-token"),
    path("posts/liked-status/", PostLikedStatusView.as_view(), name="post-liked-status"),
    path("users/<int:user_id>/liked-posts/", LikedPostsView.as_view(), name="liked-posts"),
    path("rankings/posts/likes/", PostLikeRankingView.as_view(), name="post-like-ranking"),
    path(
        "rankings/users/total-likes/",
        UserTotalLikesRankingView.as_view(),
        name="user-total-likes-ranking",
    ),
    path(
        "rankings/users/level/",
        UserLevelRankingView.as_view(),
        name="user-level-ranking",
    ),
    path(
        "rankings/users/followers/",
        UserFollowerRankingView.as_view(),
        name="user-follower-ranking",
    ),
    path("timeline/", TimelineView.as_view(), name="timeline"),
    path("search/users/", UserSearchView.as_view(), name="search-users"),
    path("search/posts/", PostSearchView.as_view(), name="search-posts"),
    path("", include(router.urls)),
]
