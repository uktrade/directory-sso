import pytest

from sso.user import forms


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
