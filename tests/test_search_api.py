import pytest

from .factories import PostFactory, UserFactory


@pytest.mark.django_db
def test_user_search_orders_by_total_likes(api_client, user, another_user):
    third = UserFactory(username="user3")

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
    first = PostFactory(user=user, context="hello world", like_count=1)
    second = PostFactory(user=user, context="hello again", like_count=5)

    response = api_client.get("/api/search/posts/", {"q": "hello"})

    assert response.status_code == 200
    contexts = [item["context"] for item in response.data["results"]]
    assert contexts == ["hello again", "hello world"]


@pytest.mark.django_db
def test_post_search_requires_query(api_client):
    response = api_client.get("/api/search/posts/")

    assert response.status_code == 200
    assert response.data["results"] == []
