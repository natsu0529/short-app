import pytest
from rest_framework.test import APIRequestFactory

from api.serializers import FollowSerializer, PostSerializer
from post.models import Post


@pytest.mark.django_db
def test_follow_serializer_rejects_self_follow(user):
    request = APIRequestFactory().post("/api/follows/")
    request.user = user
    serializer = FollowSerializer(
        data={"aim_user_id": user.pk},
        context={"request": request},
    )

    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors


@pytest.mark.django_db
def test_post_serializer_returns_nested_user(user):
    post = Post.objects.create(user=user, context="hello world")
    serializer = PostSerializer(post)

    assert serializer.data["user"]["user_id"] == user.user_id
    assert serializer.data["context"] == "hello world"
