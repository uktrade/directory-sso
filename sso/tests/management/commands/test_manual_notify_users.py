import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


@pytest.mark.django_db
def test_manual_notify_users_command_with_multiple_users(
    user,
    thirty_day_notification_user,
    fourteen_day_notification_user,
    seven_day_notification_user,
    zero_day_notification_user,
    mock_adhoc_notification_client,
):
    """
    Multiple user setup and one user is active and other old enough to get notification
    four notification should be generated
    """
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 5

    # one old user deleted as per data retention policy
    call_command('manual_notify_users', 30)

    assert mock_adhoc_notification_client.send_email_notification.called
    assert mock_adhoc_notification_client.send_email_notification.call_count == 1


@pytest.mark.django_db
def test_manual_notify_users_command_for_active_users(user, mock_adhoc_notification_client):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 1

    # No user should be notified as it active user
    call_command('manual_notify_users', 30)

    assert mock_adhoc_notification_client.send_email_notification.called is False
    assert mock_adhoc_notification_client.send_email_notification.call_count == 0


@pytest.mark.django_db
def test_manual_notify_users_command_for_valid_response(inactive_user, mock_adhoc_notification_client):
    User = get_user_model()  # noqa
    total_users = User.objects.count()
    test_user = User.objects.first()

    assert total_users == 1

    call_command('manual_notify_users', 30)

    test_user.refresh_from_db()
    assert test_user.inactivity_notification == 1


@pytest.mark.django_db
def test_manual_notify_users_command_for_invalid_api_response(inactive_user, mock_adhoc_notification_bad_client):

    User = get_user_model()  # noqa
    total_users = User.objects.count()
    test_user = User.objects.first()
    assert total_users == 1

    with pytest.raises(Exception) as exec_info:
        call_command('manual_notify_users', 30)

    assert str(exec_info.value) == f'Something went wrong in GOV notification service while notifying {test_user}'
    test_user.refresh_from_db()
    assert test_user.inactivity_notification == 0


@pytest.mark.django_db
def test_manual_notify_users_command_test_zero_day_notification_note(
    zero_day_notification_adhoc_user, mock_adhoc_notification_client
):
    User = get_user_model()  # noqa
    total_users = User.objects.count()

    assert total_users == 1

    call_command('manual_notify_users', 0)

    assert mock_adhoc_notification_client.send_email_notification.called
    assert mock_adhoc_notification_client.send_email_notification.call_count == 1
    assert (
        mock_adhoc_notification_client.send_email_notification.call_args[1]['personalisation']['day_variation']
        == 'today'
    )
