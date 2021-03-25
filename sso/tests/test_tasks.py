from unittest import mock

from django.test.utils import override_settings

from sso import tasks


@override_settings(
    FEATURE_REDIS_USE_SSL=True,
)
@mock.patch('sso.tasks.call_command')
def test_notify_users_task(mocked_call_command):
    tasks.notify_users()
    mocked_call_command.assert_called_once()


@override_settings(
    FEATURE_REDIS_USE_SSL=True,
)
@mock.patch('sso.tasks.call_command')
def test_archive_users_task(mocked_call_command):
    tasks.archive_users()
    mocked_call_command.assert_called_once()
