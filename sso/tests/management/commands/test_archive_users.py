from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


class MockResponse:
    status_code = 204


class MockInvalidResponse:
    status_code = 404


@pytest.mark.django_db
def test_archive_command_users(active_user, old_user):
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
def test_archive_command_users_for_old_user_without_notification(active_user, old_user_with_no_notification):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 2

    # no user should be archived as no final notification for this user
    with patch('directory_api_client.company.CompanyAPIClient.delete_company_by_sso_id') as mock_call:
        mock_call.return_value = MockResponse
        # one old user deleted as per data retention policy
        call_command('archive_users')

    total_users = User.objects.count()

    assert total_users == 2
    assert mock_call.called is False
    assert mock_call.call_count == 0


@pytest.mark.django_db
def test_archive_command_for_recent_users(active_user):
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
def test_archive_command_for_invalid_api_response(active_user, old_user):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 2

    with pytest.raises(Exception):
        with patch('directory_api_client.company.CompanyAPIClient.delete_company_by_sso_id') as mock_call:
            mock_call.return_value = MockInvalidResponse
            # no users should be deleted
            call_command('archive_users')
