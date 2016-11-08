import pytest

from sso.user import forms

from django.forms.fields import Field


REQUIRED_MESSAGE = Field.default_error_messages['required']


def test_signup_form_email_twice():
    form = forms.SignupForm()

    assert 'email' in form.fields
    assert 'email2' in form.fields


def test_signup_form_customization():
    form = forms.SignupForm()

    assert form.fields['password2'].label == 'Confirm password:'


def test_login_form_customization():
    form = forms.LoginForm()

    assert form.fields['remember'].label == 'Remember me:'


def test_change_password_form_customization():
    form = forms.ChangePasswordForm()

    assert form.fields['password2'].label == 'Confirm password:'


@pytest.mark.django_db
def test_password_reset_form_customization():
    form = forms.ResetPasswordForm(
        data={'email': 'a@example.com'}
    )
    expected = forms.ResetPasswordForm.NO_ACCOUNT

    assert form.is_valid() is False
    assert form.errors['email'] == [expected]


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
