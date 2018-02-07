import pytest
from unittest.mock import patch
from allauth.account.models import EmailAddress

from sso.user.models import User


@pytest.fixture(autouse=True)
def mock_signature_checker():
    mock_path = 'sigauth.utils.RequestSignatureChecker.test_signature'
    patcher = patch(mock_path, return_value=True)
    patcher.start()
    yield
    patcher.stop()


@pytest.fixture
def active_user():
    user = User.objects.create_user(
        email='dev@example.com',
        password='password',
        is_active=True,
        id=11
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
        id=1,
        user_id=user.id
    )
    return user


@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        email='inactive@user.com',
        password='password',
        is_active=False,
        id=22
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
        id=2,
        user_id=user.id
    )
    return user
