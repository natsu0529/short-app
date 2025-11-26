from datetime import timedelta

import pytest
from django.utils import timezone

from follow.models import Follow
from post.models import Post

from .factories import PostFactory, UserFactory


@pytest.mark.django_db
def test_post_list_returns_created_post(api_client, user):
    PostFactory(user=user, context="first post")

    response = api_client.get("/api/posts/")

    assert response.status_code == 200
    assert response.data[0]["context"] == "first post"


@pytest.mark.django_db
def test_post_create_requires_authentication(api_client):
    response = api_client.post("/api/posts/", {"context": "no auth"})

    assert response.status_code == 401


@pytest.mark.django_db
def test_post_create_uses_authenticated_user(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post("/api/posts/", {"context": "new post"})

    assert response.status_code == 201
    assert Post.objects.filter(context="new post", user=user).exists()


@pytest.mark.django_db
def test_follow_create_blocks_self_follow(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.post("/api/follows/", {"aim_user_id": user.pk})

    assert response.status_code == 400
    assert not Follow.objects.exists()


@pytest.mark.django_db
def test_timeline_latest_returns_posts_in_order(api_client, user, another_user):
    old = PostFactory(user=user, context="old")
    new = PostFactory(user=another_user, context="new")

    response = api_client.get("/api/timeline/", {"tab": "latest"})

    assert response.status_code == 200
    results = response.data["results"]
    assert [post["post_id"] for post in results] == [new.post_id, old.post_id]


@pytest.mark.django_db
def test_timeline_popular_filters_recent_posts_and_orders(api_client, user):
    within_window_high = PostFactory(user=user, context="win high", like_count=10)
    within_window_low = PostFactory(user=user, context="win low", like_count=2)
    outside_window = PostFactory(
        user=user,
        context="old popular",
        like_count=100,
        time=timezone.now() - timedelta(hours=30),
    )

    response = api_client.get("/api/timeline/", {"tab": "popular"})

    assert response.status_code == 200
    contexts = [post["context"] for post in response.data["results"]]
    assert contexts == ["win high", "win low"]


@pytest.mark.django_db
def test_timeline_following_requires_auth(api_client, user, another_user):
    PostFactory(user=another_user, context="followed")
    PostFactory(user=user, context="own")
    Follow.objects.create(user=user, aim_user=another_user)

    response = api_client.get("/api/timeline/", {"tab": "following"})

    assert response.status_code == 200
    assert response.data["results"] == []

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/timeline/", {"tab": "following"})

    assert [post["context"] for post in response.data["results"]] == ["followed"]


@pytest.mark.django_db
def test_user_profile_includes_rank(api_client, user, another_user):
    third = UserFactory(username="user3")

    another_user.stats.total_likes_received = 15
    another_user.stats.save()
    user.stats.total_likes_received = 10
    user.stats.save()
    third.stats.total_likes_received = 10
    third.stats.save()

    response = api_client.get("/api/users/")

    assert response.status_code == 200
    ranks = {item["username"]: item["rank"] for item in response.data}
    assert ranks[another_user.username] == 1
    assert ranks[user.username] == 2
    assert ranks[third.username] == 2
    assert "stats" in response.data[0]


@pytest.mark.django_db
def test_users_me_returns_authenticated_user(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/users/me/")

    assert response.status_code == 200
    assert response.data["user_id"] == user.user_id
    assert response.data["username"] == user.username
    assert response.data["rank"] == 1
    assert "stats" in response.data


@pytest.mark.django_db
def test_users_me_requires_authentication(api_client):
    response = api_client.get("/api/users/me/")

    assert response.status_code == 401
