import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command


@pytest.fixture
def user():
    User = get_user_model()  # noqa
    user = User.objects.create(email='abc@xyz.com')
    yield user
    user.delete()


@pytest.fixture
def old_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def@xyz.com')
    # user last_login around 4 years ago
    user.last_login = datetime.now() - timedelta(days=4 * 365)
    # user created 5 years ago
    user.created = datetime.now() - timedelta(days=5 * 365)
    user.save()
    yield user
    user.delete()


class MockResponse:
    status_code = 204


class MockInvalidResponse:
    status_code = 404


@pytest.mark.django_db
def test_archive_command_users(user, old_user):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 2

    with patch('directory_api_client.company.CompanyAPIClient.delete_company_by_sso_id') as mock_call:
        mock_call.return_value = MockResponse
        # one old user deleted as per data retention policy
        call_command('archive_users')

    total_users = User.objects.count()

    assert total_users == 1
    assert mock_call.called
    assert mock_call.call_count == 1


@pytest.mark.django_db
def test_archive_command_for_recent_users(user):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 1

    with patch('directory_api_client.company.CompanyAPIClient.delete_company_by_sso_id') as mock_call:
        mock_call.return_value = MockResponse
        # no users should be deleted
        call_command('archive_users')

    total_users = User.objects.count()

    assert total_users == 1
    assert mock_call.not_called
    assert mock_call.call_count == 0


@pytest.mark.django_db
def test_archive_command_for_invalid_api_response(user, old_user):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 2

    with pytest.raises(Exception):
        with patch('directory_api_client.company.CompanyAPIClient.delete_company_by_sso_id') as mock_call:
            mock_call.return_value = MockInvalidResponse
            # no users should be deleted
            call_command('archive_users')
