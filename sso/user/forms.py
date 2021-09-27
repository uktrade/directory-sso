import allauth.account.forms
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import filter_users_by_email
from allauth.utils import set_form_field_order
from directory_components import forms
from directory_constants import urls
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import TextInput
from django.utils.safestring import mark_safe

from sso.user.fields import PasswordField
from sso.user.utils import notify_already_registered


class SignupForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.SignupForm):
    PASSWORD_HELP_TEXT = (
        '<p>Your password must:</p>'
        '<ul class="list list-bullet">'
        '<li>be at least 10 characters</li>'
        '<li>contain at least one letter</li>'
        '<li>contain at least one number</li>'
        '<li>not contain the word "password"</li>'
        '</ul>'
    )
    terms_agreed = forms.BooleanField(
        label=mark_safe(
            'Tick this box to accept the '
            f'<a href="{urls.domestic.TERMS_AND_CONDITIONS}" target="_blank">terms and '
            'conditions</a> of the great.gov.uk service.'
        )
    )
    field_order = [
        'email',
        'email2',
        'password1',
        'password2',
        'terms_agreed',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            label='Email',
            label_suffix='',
            widget=TextInput(
                attrs={
                    'type': 'email',
                    'autofocus': 'autofocus',
                    'autocomplete': 'new-password',
                }
            ),
        )

        self.fields['email2'] = forms.EmailField(
            label='Confirm email',
            label_suffix='',
            widget=TextInput(
                attrs={
                    'type': 'email',
                    'autofocus': 'autofocus',
                    'autocomplete': 'new-password',
                }
            ),
        )
        self.fields['password1'] = PasswordField(
            label="Password",
            label_suffix='',
            help_text=mark_safe(self.PASSWORD_HELP_TEXT),
        )
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'] = PasswordField(
            label="Confirm password",
            label_suffix='',
        )
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'
        set_form_field_order(self, self.field_order)

    def clean_email(self):
        value = super().clean_email()
        if EmailAddress.objects.filter(email__iexact=value).exists():
            notify_already_registered(email=value)
        return value


class LoginForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.LoginForm):
    password = PasswordField(
        label="Password",
        label_suffix='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password'].widget.attrs['placeholder'] = ''
        self.fields['login'] = forms.EmailField(
            label='Email',
            label_suffix='',
            widget=TextInput(
                attrs={
                    'type': 'email',
                    'autofocus': 'autofocus',
                    'autocomplete': 'new-password',
                }
            ),
        )


class UserForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.UserForm):
    pass


class AddEmailForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.AddEmailForm):
    pass


class ChangePasswordForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oldpassword'] = PasswordField(
            label="Password",
            label_suffix='',
        )
        self.fields['password1'] = PasswordField(
            label="New password",
            label_suffix='',
        )
        self.fields['password2'] = PasswordField(
            label="Confirm password",
            label_suffix='',
        )


class SetPasswordForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.SetPasswordForm):
    pass


class ResetPasswordForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            label='Email',
            label_suffix='',
            widget=TextInput(
                attrs={
                    'type': 'email',
                    'autofocus': 'autofocus',
                    'autocomplete': 'new-password',
                }
            ),
        )

    def clean_email(self):
        """Overrides allauth's method for security reasons.

        Validation for whether a user/email exists has been removed.
        This prevents potential attackers from finding out which emails
        are registered in our system by attempting to submit this form.

        """
        email = self.cleaned_data["email"]
        email = get_adapter().clean_email(email)
        # allauth sends reset emails to all users in self.users.
        # If there are none it will not send any emails
        self.users = filter_users_by_email(email)
        return self.cleaned_data["email"]


class ResetPasswordKeyForm(forms.DirectoryComponentsFormMixin, allauth.account.forms.ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'] = PasswordField(
            label="New password",
            label_suffix='',
        )
        self.fields['password2'] = PasswordField(
            label="Confirm password",
            label_suffix='',
        )

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except ValidationError as error:
            self.add_error('password1', error)
        return password1
