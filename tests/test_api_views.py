from datetime import timedelta

import pytest
from django.utils import timezone

from follow.models import Follow
from post.models import Post


@pytest.mark.django_db
def test_post_list_returns_created_post(api_client, user):
    Post.objects.create(user=user, context="first post")

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
    old = Post.objects.create(user=user, context="old")
    new = Post.objects.create(user=another_user, context="new")

    response = api_client.get("/api/timeline/", {"tab": "latest"})

    assert response.status_code == 200
    results = response.data["results"]
    assert [post["post_id"] for post in results] == [new.post_id, old.post_id]


@pytest.mark.django_db
def test_timeline_popular_filters_recent_posts_and_orders(api_client, user):
    within_window_high = Post.objects.create(user=user, context="win high")
    within_window_high.like_count = 10
    within_window_high.save(update_fields=["like_count"])

    within_window_low = Post.objects.create(user=user, context="win low")
    within_window_low.like_count = 2
    within_window_low.save(update_fields=["like_count"])

    outside_window = Post.objects.create(user=user, context="old popular")
    outside_window.like_count = 100
    outside_window.time = timezone.now() - timedelta(hours=30)
    outside_window.save(update_fields=["like_count", "time"])

    response = api_client.get("/api/timeline/", {"tab": "popular"})

    assert response.status_code == 200
    contexts = [post["context"] for post in response.data["results"]]
    assert contexts == ["win high", "win low"]


@pytest.mark.django_db
def test_timeline_following_requires_auth(api_client, user, another_user):
    Post.objects.create(user=another_user, context="followed")
    Post.objects.create(user=user, context="own")
    Follow.objects.create(user=user, aim_user=another_user)

    response = api_client.get("/api/timeline/", {"tab": "following"})

    assert response.status_code == 200
    assert response.data["results"] == []

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/timeline/", {"tab": "following"})

    assert [post["context"] for post in response.data["results"]] == ["followed"]
