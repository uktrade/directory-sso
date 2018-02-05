import pytest
from django.conf import settings
from unittest.mock import patch

from sso.user import models


@pytest.fixture(autouse=True)
def mock_signature_checker():
    mock_path = "sigauth.utils.RequestSignatureChecker.test_signature"
    patcher = patch(mock_path, return_value=True)
    patcher.start()
    yield
    patcher.stop()


@pytest.fixture
def test_api_auth_token():
    return settings.TEST_API_AUTH_TOKEN


@pytest.fixture
def active_user():
    return models.User.objects.create_user(
        email="dev@example.com",
        password="password",
        is_active=True,
        id=1
    )


@pytest.fixture
def inactive_user():
    return models.User.objects.create_user(
        email="inactive@user.com",
        password="password",
        is_active=False,
        id=2
    )
