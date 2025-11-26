import pytest
from datetime import timedelta
from django.utils import timezone

from .factories import LikeFactory, PostFactory, UserFactory


@pytest.mark.django_db
def test_post_like_ranking_orders_by_like_count(api_client, user):
    high = PostFactory(user=user, context="high", like_count=10)
    low = PostFactory(user=user, context="low", like_count=2)

    response = api_client.get("/api/rankings/posts/likes/")

    assert response.status_code == 200
    contexts = [item["context"] for item in response.data["results"]]
    assert contexts == ["high", "low"]
    assert response.data["results"][0]["post_id"] == high.post_id


@pytest.mark.django_db
def test_post_like_ranking_supports_24h_filter(api_client, user):
    old = PostFactory(
        user=user, context="old", like_count=50, time=timezone.now() - timedelta(days=3)
    )
    recent = PostFactory(user=user, context="recent", like_count=5)
    PostFactory(user=user, context="recent2", like_count=10)

    response = api_client.get("/api/rankings/posts/likes/", {"range": "24h"})

    assert response.status_code == 200
    contexts = [item["context"] for item in response.data["results"]]
    assert "old" not in contexts
    assert contexts[0] == "recent2"
    assert recent.post_id in [item["post_id"] for item in response.data["results"]]


@pytest.mark.django_db
def test_user_total_likes_ranking(api_client):
    first = UserFactory()
    second = UserFactory()
    first.stats.total_likes_received = 20
    first.stats.save()
    second.stats.total_likes_received = 5
    second.stats.save()

    response = api_client.get("/api/rankings/users/total-likes/")

    assert response.status_code == 200
    usernames = [item["username"] for item in response.data["results"]]
    assert usernames[:2] == [first.username, second.username]


@pytest.mark.django_db
def test_user_level_ranking(api_client):
    low = UserFactory()
    high = UserFactory()
    low.user_level = 1
    low.save()
    high.user_level = 10
    high.save()

    response = api_client.get("/api/rankings/users/level/")

    assert response.status_code == 200
    usernames = [item["username"] for item in response.data["results"]]
    assert usernames.index(high.username) < usernames.index(low.username)


@pytest.mark.django_db
def test_user_follower_ranking(api_client):
    first = UserFactory()
    second = UserFactory()
    first.stats.follower_count = 50
    first.stats.save()
    second.stats.follower_count = 10
    second.stats.save()

    response = api_client.get("/api/rankings/users/followers/")

    assert response.status_code == 200
    usernames = [item["username"] for item in response.data["results"]]
    assert usernames[:2] == [first.username, second.username]


@pytest.mark.django_db
def test_post_like_ranking_includes_is_liked(api_client, user):
    liked = PostFactory()
    LikeFactory(user=user, post=liked)
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/rankings/posts/likes/")

    assert response.status_code == 200
    row = next(item for item in response.data["results"] if item["post_id"] == liked.post_id)
    assert row["is_liked"] is True
