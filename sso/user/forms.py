from django.forms import BooleanField
from django.utils.safestring import mark_safe

from allauth.account import forms
from allauth.account.adapter import get_adapter
from allauth.account.utils import filter_users_by_email
from allauth.utils import set_form_field_order

from directory_constants.constants import urls

from sso.user.widgets import CheckboxWithInlineLabel


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class SignupForm(IndentedInvalidFieldsMixin, forms.SignupForm):
    PASSWORD_HELP_TEXT = 'Must contain at least 10 characters.'
    terms_agreed = BooleanField(
        label='',
        widget=CheckboxWithInlineLabel(
            label=mark_safe(
                'Tick this box to accept the '
                '<a href="{url}" target="_blank">terms and '
                'conditions</a> of the great.gov.uk service.'.format(
                    url=urls.INFO_TERMS_AND_CONDITIONS)
            )
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
        self.fields['email'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['email'].widget.attrs['placeholder'] = 'Email address'
        self.fields['email'].label = 'Email:'
        self.fields['email2'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['email2'].widget.attrs['placeholder'] = (
            'Email address confirmation'
        )
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

        self.fields['password1'].help_text = self.PASSWORD_HELP_TEXT
        self.fields['password2'].label = 'Confirm password:'
        self.fields['email2'].label = 'Confirm email:'
        set_form_field_order(self, self.field_order)


class LoginForm(IndentedInvalidFieldsMixin, forms.LoginForm):

    remember = BooleanField(
        label='',
        required=False,
        widget=CheckboxWithInlineLabel(
            label='Remember me'
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['login'].label = 'Email'
        self.fields['login'].widget.attrs['placeholder'] = 'Email address'

        self.fields['password'].widget.attrs['autocomplete'] = 'new-password'


class UserForm(IndentedInvalidFieldsMixin, forms.UserForm):
    pass


class AddEmailForm(IndentedInvalidFieldsMixin, forms.AddEmailForm):
    pass


class ChangePasswordForm(IndentedInvalidFieldsMixin, forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = 'Confirm password:'


class SetPasswordForm(IndentedInvalidFieldsMixin, forms.SetPasswordForm):
    pass


class ResetPasswordForm(IndentedInvalidFieldsMixin, forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autocomplete'] = 'new-password'

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


class ResetPasswordKeyForm(IndentedInvalidFieldsMixin,
                           forms.ResetPasswordKeyForm):
    pass
