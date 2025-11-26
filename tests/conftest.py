import pytest
from rest_framework.test import APIClient

from .factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory(username="user1")


@pytest.fixture
def another_user(db):
    return UserFactory(username="user2")


@pytest.fixture
def api_client():
    return APIClient()
