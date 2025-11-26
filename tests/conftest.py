import pytest
from rest_framework.test import APIClient

from accounts.models import CustomUser


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        username="user1",
        password="testpass123",
        email="user1@example.com",
        user_name="User One",
        user_mail="user1@example.com",
    )


@pytest.fixture
def another_user(db):
    return CustomUser.objects.create_user(
        username="user2",
        password="testpass123",
        email="user2@example.com",
        user_name="User Two",
        user_mail="user2@example.com",
    )


@pytest.fixture
def api_client():
    return APIClient()
