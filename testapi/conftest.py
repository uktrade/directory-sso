from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from sso.user import models


@pytest.fixture(autouse=True)
def mock_signature_checker():
    mock_path = 'sigauth.utils.RequestSignatureChecker.test_signature'
    patcher = patch(mock_path, return_value=True)
    patcher.start()
    yield
    patcher.stop()


@pytest.fixture
def test_api_auth_token():
    return "debug"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return models.User.objects.create_user(
        email='dev@example.com',
        password='password',
    )


@pytest.fixture
def authed_client(client, user):
    client.force_login(user)
    return client
