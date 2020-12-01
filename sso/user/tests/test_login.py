from unittest import mock

import pytest
from django.contrib.auth import authenticate

from sso.user.models import User


@pytest.mark.django_db
@mock.patch.object(User, 'check_password', return_value=False)
def test_check_password_call_count(mocked_check_password, adminsuperuser):
    """
    Count the number of times the authentication backend uses the
    check_password method

    The failed login attempts counter is hooked to the check_password()
    method at the User model level.

    Some, but not necessarily all, of the authentication backends call this
    method in their authenticate() method.

    As of today (28 Nov 2017) 2 auth backends (out of 3 we use) in our settings
    are calling check_password() ('django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend').

    This test is here to fail if we add a new backend that does use the
    method so to make our calculation more explicit.

    The mock returns False so all the backends are used and counted.

    https://github.com/django/django/blob/1.11.7/django/contrib/auth/__init__.py#L68
    https://github.com/django/django/blob/1.11.7/django/contrib/auth/__init__.py#L115
    """
    authenticate(username='foo@bar.com', password='foobarb1sdfdsfgds')
    assert mocked_check_password.call_count == 2


@pytest.mark.django_db
def test_incorrect_authentication_increment_counter(adminsuperuser):
    assert adminsuperuser.failed_login_attempts == 0
    authenticate(username='foo@bar.com', password='foobarb1sdfdsfgds')
    adminsuperuser.refresh_from_db()
    assert adminsuperuser.failed_login_attempts == 2


@pytest.mark.django_db
def test_correct_authentication_resets_counter(adminsuperuser):
    assert adminsuperuser.failed_login_attempts == 0
    authenticate(username='foo@bar.com', password='foobarb1sdfdsfgds')
    adminsuperuser.refresh_from_db()
    assert adminsuperuser.failed_login_attempts == 2

    # now login with the right credentials
    authenticate(username='foo@bar.com', password='3whitehallplace')
    adminsuperuser.refresh_from_db()
    assert adminsuperuser.failed_login_attempts == 0


@pytest.mark.django_db
@mock.patch('sso.user.models.send_mail')
def test_incorrect_auth_threshold_email_trigger(mock_send_mail, adminsuperuser, settings):
    settings.SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL = 'foo@bar.com'
    assert adminsuperuser.failed_login_attempts == 0
    for i in range(settings.SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS):
        authenticate(username='foo@bar.com', password='foobarb1sdfdsfgds')

    assert mock_send_mail.call_count == 1
    assert mock_send_mail.call_args == mock.call(
        from_email='debug',
        message='foo@bar.com tried to login 10 times',
        recipient_list=['foo@bar.com'],
        subject='Suspicious activity on SSO',
    )
