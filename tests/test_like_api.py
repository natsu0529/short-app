import pytest

from .factories import LikeFactory, PostFactory, UserFactory


@pytest.mark.django_db
def test_like_create_increments_counts(api_client, user, another_user):
    post = PostFactory(user=another_user)
    api_client.force_authenticate(user=user)

    response = api_client.post("/api/likes/", {"post_id": post.post_id})

    assert response.status_code == 201
    post.refresh_from_db()
    another_user.stats.refresh_from_db()
    user.stats.refresh_from_db()
    assert post.like_count == 1
    assert another_user.stats.total_likes_received == 1
    assert user.stats.total_likes_given == 1


@pytest.mark.django_db
def test_like_delete_decrements_counts(api_client, user, another_user):
    post = PostFactory(user=another_user, like_count=1)
    like = LikeFactory(user=user, post=post)
    another_user.stats.total_likes_received = 1
    another_user.stats.save()
    user.stats.total_likes_given = 1
    user.stats.save()
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/likes/{like.id}/")

    assert response.status_code == 204
    post.refresh_from_db()
    another_user.stats.refresh_from_db()
    user.stats.refresh_from_db()
    assert post.like_count == 0
    assert another_user.stats.total_likes_received == 0
    assert user.stats.total_likes_given == 0


@pytest.mark.django_db
def test_like_prevents_duplicate(api_client, user, another_user):
    post = PostFactory(user=another_user)
    LikeFactory(user=user, post=post)
    api_client.force_authenticate(user=user)

    response = api_client.post("/api/likes/", {"post_id": post.post_id})

    assert response.status_code == 400


@pytest.mark.django_db
def test_liked_posts_list(api_client, user):
    first = PostFactory(context="first liked")
    second = PostFactory(context="second liked")
    LikeFactory(user=user, post=first)
    LikeFactory(user=user, post=second)

    response = api_client.get(f"/api/users/{user.user_id}/liked-posts/")

    assert response.status_code == 200
    contexts = [item["context"] for item in response.data["results"]]
    assert contexts == ["second liked", "first liked"]


@pytest.mark.django_db
def test_liked_status_api(api_client, user):
    liked = PostFactory()
    not_liked = PostFactory()
    LikeFactory(user=user, post=liked)
    api_client.force_authenticate(user=user)

    response = api_client.get(
        "/api/posts/liked-status/", {"ids": f"{liked.post_id},{not_liked.post_id}"}
    )

    assert response.status_code == 200
    assert response.data["liked_post_ids"] == [liked.post_id]


@pytest.mark.django_db
def test_liked_status_requires_auth(api_client):
    response = api_client.get("/api/posts/liked-status/", {"ids": "1"})

    assert response.status_code == 401
