import pytest

from accounts.models import CustomUser
from post.models import Post


@pytest.mark.django_db
def test_user_search_orders_by_total_likes(api_client, user, another_user):
    third = CustomUser.objects.create_user(
        username="user3",
        password="pass123",
        email="user3@example.com",
        user_name="Third User",
        user_mail="user3@example.com",
    )

    user.stats.total_likes_received = 5
    user.stats.save()
    another_user.stats.total_likes_received = 10
    another_user.stats.save()

    response = api_client.get("/api/search/users/", {"q": "user"})

    assert response.status_code == 200
    results = response.data["results"]
    assert [item["user_id"] for item in results] == [
        another_user.user_id,
        user.user_id,
        third.user_id,
    ]


@pytest.mark.django_db
def test_user_search_requires_query(api_client):
    response = api_client.get("/api/search/users/")

    assert response.status_code == 200
    assert response.data["results"] == []


@pytest.mark.django_db
def test_post_search_orders_by_like_count(api_client, user):
    first = Post.objects.create(user=user, context="hello world")
    first.like_count = 1
    first.save(update_fields=["like_count"])

    second = Post.objects.create(user=user, context="hello again")
    second.like_count = 5
    second.save(update_fields=["like_count"])

    response = api_client.get("/api/search/posts/", {"q": "hello"})

    assert response.status_code == 200
    contexts = [item["context"] for item in response.data["results"]]
    assert contexts == ["hello again", "hello world"]


@pytest.mark.django_db
def test_post_search_requires_query(api_client):
    response = api_client.get("/api/search/posts/")

    assert response.status_code == 200
    assert response.data["results"] == []
