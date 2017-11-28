import pytest
from django.contrib.auth import authenticate
from unittest import mock

from sso.user.models import User


@pytest.mark.django_db
@mock.patch.object(User, 'check_password', return_value=False)
def test_count_authentication_backends_using_check_password_method(
        mocked_check_password,
        adminsuperuser
):
    """
    The failed login attempts counter is hooked to the check_password()
    method at the User model levels.

    Some, but not necessarily all, of the authentication backends call this
    method in their authenticate() method.

    As today (28 Nov 2017) 2 auth backends (out of 3 we use) in our settings
    are calling check_password() ('django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend').

    This test is here to fail if we add a new backend that does use the
    method so to make our calculations more explicit.

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
