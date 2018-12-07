from unittest import mock
from unittest.mock import patch

from allauth.account.models import EmailAddress
from directory_constants.constants import urls
import pytest

from django.forms.fields import Field
from django.core.validators import EmailValidator

from sso.adapters import PASSWORD_RESET_TEMPLATE_ID
from sso.user import forms
from sso.user.models import User


REQUIRED_MESSAGE = Field.default_error_messages['required']
INVALID_EMAIL_MESSAGE = EmailValidator.message


@pytest.fixture
def verified_user():
    user = User.objects.create_user(
        email='verified@example.com',
        password='password',
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True
    )
    return user


def test_signup_form_email_twice():
    form = forms.SignupForm()

    assert 'email' in form.fields
    assert 'email2' in form.fields


def test_signup_form_customization():
    form = forms.SignupForm()

    assert form.fields['password2'].label == 'Confirm password:'
    assert form.fields['password1'].help_text == form.PASSWORD_HELP_TEXT


def test_change_password_form_customization():
    form = forms.ChangePasswordForm()

    assert form.fields['password2'].label == 'Confirm password:'


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_form_accepts_nonexisting_email_without_sending(
        mocked_notification_client, rf
):
    form = forms.ResetPasswordForm(
        data={'email': 'nonexistingemail@example.com'}
    )
    request = rf.get('/')

    assert form.is_valid() is True
    form.save(request)
    assert mocked_notification_client().send_email_notification.called is False


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_form_accepts_existing_email_and_sends(
    mocked_notification_client, rf, verified_user
):
    form = forms.ResetPasswordForm(
        data={'email': verified_user.email}
    )
    request = rf.get('/')

    assert form.is_valid() is True
    form.save(request)
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='verified@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=PASSWORD_RESET_TEMPLATE_ID
    )


def test_password_reset_form_invalid_email():
    form = forms.ResetPasswordForm(
        data={'email': 'this is not an email'}
    )

    assert form.is_valid() is False
    assert INVALID_EMAIL_MESSAGE in form.errors['email']


def test_password_reset_form_email_required():
    form = forms.ResetPasswordForm(
        data={'email': ''}
    )

    assert form.is_valid() is False
    assert REQUIRED_MESSAGE in form.errors['email']


def test_signup_rejects_missing_terms_agreed():
    form = forms.SignupForm(data={})

    assert form.is_valid() is False
    assert form.errors['terms_agreed'] == [REQUIRED_MESSAGE]


def test_signup_accepts_present_terms_agreed():
    form = forms.SignupForm(data={'terms_agreed': True})

    assert form.is_valid() is False
    assert 'terms_agreed' not in form.errors


def test_signup_field_order():
    expected_field_order = [
        'email',
        'email2',
        'password1',
        'password2',
        'terms_agreed',
    ]
    assert forms.SignupForm.field_order == expected_field_order


def test_signup_rejects_password_length_less_than_ten():
    for i in range(1, 10):
        form = forms.SignupForm(data={
            'password1': '*' * i
        })
        expected = (
            'This password is too short. It must contain at least 10 '
            'characters.'
        )

        assert form.is_valid() is False
        assert form.errors['password1'] == [expected]


def test_signup_accepts_password_length_ten_or_more():
    form = forms.SignupForm(data={
        'password1': '*' * 10
    })

    assert form.is_valid() is False
    assert 'password1' not in form.errors


def test_signup_autocomplete():
    # http://stackoverflow.com/a/30976223/904887
    form = forms.SignupForm()
    for name in ['email', 'email2', 'password1', 'password2']:
        assert form.fields[name].widget.attrs['autocomplete'] == 'new-password'


def test_login_autocomplete():
    # http://stackoverflow.com/a/30976223/904887
    form = forms.LoginForm()
    for name in ['login', 'password']:
        assert form.fields[name].widget.attrs['autocomplete'] == 'new-password'


def test_password_reset_autocomplete():
    # http://stackoverflow.com/a/30976223/904887
    form = forms.ResetPasswordForm()
    assert form.fields['email'].widget.attrs['autocomplete'] == 'new-password'


@patch('sso.user.forms.NotificationsAPIClient')
def test_notify_already_registered(mocked_notifications):
    forms.SignupForm.notify_already_registered('test@example.com')
    stub = mocked_notifications().send_email_notification
    assert stub.call_count == 1
    assert stub.call_args == mock.call(
        email_address='test@example.com',
        personalisation={
            'login_url': 'http://sso.trade.great:8003/accounts/login/',
            'password_reset_url': (
                'http://sso.trade.great:8003/accounts/password/reset/'
            ),
            'contact_us_url': urls.CONTACT_US
        },
        template_id='5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'
    )
