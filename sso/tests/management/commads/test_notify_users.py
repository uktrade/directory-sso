from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


@pytest.mark.django_db
def test_notify_command_with_multiple_users(
    user,
    thirty_day_notification_user,
    fourteen_day_notification_user,
    seven_day_notification_user,
    zero_day_notification_user,
):
    """
    Multiple user setup and one user is active and other old enough to get notification
    four notification should be generated
    """
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 5

    # one old user deleted as per data retention policy
    with patch('notifications_python_client.NotificationsAPIClient') as mock_call:

        call_command('notify_users')

        total_users = User.objects.count()

        assert total_users == 5
        assert mock_call().send_email_notification.called
        assert mock_call().send_email_notification.call_count == 4


@pytest.mark.django_db
def test_notify_command_for_active_users(user):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 1

    # No user should be notified as it active user
    with patch('notifications_python_client.NotificationsAPIClient') as mock_call:
        call_command('notify_users')

        total_users = User.objects.count()

        assert total_users == 1
        assert mock_call().send_email_notification.called is False
        assert mock_call().send_email_notification.call_count == 0
