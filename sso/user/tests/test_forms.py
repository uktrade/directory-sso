from unittest import mock
from unittest.mock import patch

import pytest
from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.validators import EmailValidator
from django.forms.fields import Field
from django.test import override_settings

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
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user


def test_signup_form_email_twice():
    form = forms.SignupForm()

    assert 'email' in form.fields
    assert 'email2' in form.fields


def test_signup_form_customization():
    form = forms.SignupForm()

    assert form.fields['password2'].label == 'Confirm password'
    assert form.fields['password1'].help_text == form.PASSWORD_HELP_TEXT


def test_account_change_password_form_customization():
    form = forms.ChangePasswordForm()

    assert form.fields['password2'].label == 'Confirm password'


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_form_accepts_nonexisting_email_without_sending(mocked_notification_client, rf):
    form = forms.ResetPasswordForm(data={'email': 'nonexistingemail@example.com'})
    request = rf.get('/')

    assert form.is_valid() is True
    form.save(request)
    assert mocked_notification_client().send_email_notification.called is False


@override_settings(FEATURE_USE_BGS_TEMPLATES=False)
@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_form_accepts_existing_email_and_sends(mocked_notification_client, rf, verified_user):
    form = forms.ResetPasswordForm(data={'email': verified_user.email})
    request = rf.get('/')

    assert form.is_valid() is True
    form.save(request)
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='verified@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID,
    )


def test_password_reset_form_invalid_email():
    form = forms.ResetPasswordForm(data={'email': 'this is not an email'})

    assert form.is_valid() is False
    assert INVALID_EMAIL_MESSAGE in form.errors['email']


def test_password_reset_form_email_required():
    form = forms.ResetPasswordForm(data={'email': ''})

    assert form.is_valid() is False
    assert REQUIRED_MESSAGE in form.errors['email']


def test_password_reset_key_form_validations_required():
    form = forms.ResetPasswordKeyForm(data={'password1': '', 'password2': ''})

    assert form.is_valid() is False
    assert REQUIRED_MESSAGE in form.errors['password1']
    assert REQUIRED_MESSAGE in form.errors['password2']


def test_password_reset_key_form_validations_mismatching():
    mismatching_message = 'You must type the same password each time.'
    form = forms.ResetPasswordKeyForm(data={'password1': 'onetwothree123', 'password2': 'threetwoone321'})

    assert form.is_valid() is False
    assert mismatching_message in form.errors['password2']


def test_password_reset_key_form_validations_too_short():
    too_short_message = 'This password is too short. It must contain at least 10 characters.'
    form = forms.ResetPasswordKeyForm(data={'password1': 'one1', 'password2': 'one1'})

    assert form.is_valid() is False
    assert too_short_message in form.errors['password1']


def test_password_reset_key_form_validations_too_common():
    too_common_message = 'This password is too common.'
    form = forms.ResetPasswordKeyForm(data={'password1': 'password123', 'password2': 'password123'})

    assert form.is_valid() is False
    assert too_common_message in form.errors['password1']


def test_password_reset_key_form_validations_entirely_numeric():
    entirely_numeric_message = 'This password is entirely numeric.'
    form = forms.ResetPasswordKeyForm(data={'password1': '0123456789', 'password2': '0123456789'})

    assert form.is_valid() is False
    assert entirely_numeric_message in form.errors['password1']


def test_password_reset_key_form_validations_valid():
    form = forms.ResetPasswordKeyForm(data={'password1': 'onetwothree1', 'password2': 'onetwothree1'})

    assert form.is_valid() is True


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
        form = forms.SignupForm(data={'password1': '*' * i})
        expected = 'This password is too short. It must contain at least 10 characters.'

        assert form.is_valid() is False
        assert expected in form.errors['password1']


def test_signup_accepts_password_length_ten_or_more():
    form = forms.SignupForm(data={'password1': 'ZaronZ0xos'})

    assert form.is_valid() is False
    assert 'password1' not in form.errors


@pytest.mark.parametrize('name', ['email', 'email2', 'password1', 'password2'])
def test_signup_autocomplete(name):
    # http://stackoverflow.com/a/30976223/904887
    form = forms.SignupForm()
    assert form.fields[name].widget.attrs['autocomplete'] == 'new-password'


@pytest.mark.parametrize('name', ['login', 'password'])
def test_login_autocomplete(name):
    # http://stackoverflow.com/a/30976223/904887
    form = forms.LoginForm()
    assert form.fields[name].widget.attrs['autocomplete'] == 'new-password'


def test_password_reset_autocomplete():
    # http://stackoverflow.com/a/30976223/904887
    form = forms.ResetPasswordForm()
    assert form.fields['email'].widget.attrs['autocomplete'] == 'new-password'
