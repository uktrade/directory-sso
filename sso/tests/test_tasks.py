from unittest import mock

import pytest
from django.test.utils import override_settings

from sso import tasks
from sso.user.tests.factories import UserFactory, UserProfileFactory


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


@mock.patch('sso.management.commands.obsfucate_personal_details.Command.mask_user_profile')
@mock.patch('sso.management.commands.obsfucate_personal_details.Command.mask_user')
@pytest.mark.django_db
def test_obsfucate_personal_details(mock_mask_user, mock_mask_user_profile):
    UserFactory()
    UserProfileFactory()
    tasks.obsfucate_personal_details()
    assert mock_mask_user.call_count == 2
    assert mock_mask_user_profile.call_count == 1
