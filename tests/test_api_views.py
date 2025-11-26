import pytest

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
