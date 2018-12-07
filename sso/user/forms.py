from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from allauth.account import forms
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import filter_users_by_email
from allauth.utils import set_form_field_order
from directory_constants.constants import urls
from directory_components import fields
from notifications_python_client import NotificationsAPIClient


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class SignupForm(IndentedInvalidFieldsMixin, forms.SignupForm):
    PASSWORD_HELP_TEXT = (
        'Your password must:'
        '<ul>'
        '<li>be at least 10 characters</li>'
        '<li>contain at least one letter</li>'
        '<li>contain at least one number</li>'
        '<li>not contain the word "password"</li>'
        '</ul>'
    )
    terms_agreed = fields.BooleanField(
        label=mark_safe(
            'Tick this box to accept the '
            f'<a href="{urls.TERMS_AND_CONDITIONS}" target="_blank">terms and '
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
        self.fields['email'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['email'].widget.attrs['placeholder'] = 'Email address'
        self.fields['email'].label = 'Email:'
        self.fields['email2'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['email2'].widget.attrs['placeholder'] = (
            'Email address confirmation'
        )
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

        self.fields['password1'].help_text = mark_safe(self.PASSWORD_HELP_TEXT)
        self.fields['password2'].label = 'Confirm password:'
        self.fields['email2'].label = 'Confirm email:'
        set_form_field_order(self, self.field_order)

    @staticmethod
    def notify_already_registered(email):
        """
        To prevent account enumeration in the signup form we do not inform the
        user if the email is already registered (security requirement), instead
        we send a notification with a link to password reset.
        """
        notifications_client = NotificationsAPIClient(
            settings.GOV_NOTIFY_API_KEY
        )

        notifications_client.send_email_notification(
            email_address=email,
            template_id=settings.GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID,
            personalisation={
                'login_url': (
                    settings.SSO_BASE_URL +
                    reverse('account_login')
                ),
                'password_reset_url': (
                    settings.SSO_BASE_URL +
                    reverse('account_reset_password')
                ),
                'contact_us_url': urls.CONTACT_US
            }
        )

    def clean_email(self):
        value = super().clean_email()
        if EmailAddress.objects.filter(email__iexact=value).exists():
            self.notify_already_registered(email=value)
        return value


class LoginForm(IndentedInvalidFieldsMixin, forms.LoginForm):

    remember = fields.BooleanField(
        label='Remember me',
        required=False,
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
        self.fields['email'].widget.attrs['placeholder'] = 'Email address'
        self.fields['email'].label = 'Email:'

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
