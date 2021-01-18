import hashlib

import allauth.account.forms
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import filter_users_by_email
from allauth.utils import set_form_field_order
from directory_components import forms
from directory_constants import urls
from django.conf import settings
from django.core.cache import cache
from django.forms import TextInput, ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from notifications_python_client import NotificationsAPIClient

from sso.user.fields import PasswordField


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

    @staticmethod
    def notify_already_registered(email):
        """
        To prevent account enumeration in the signup form we do not inform the
        user if the email is already registered (security requirement), instead
        we send a notification with a link to password reset.
        """
        notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)

        notifications_client.send_email_notification(
            email_address=email,
            template_id=settings.GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID,
            personalisation={
                'login_url': (settings.SSO_BASE_URL + reverse('account_login')),
                'password_reset_url': (settings.SSO_BASE_URL + reverse('account_reset_password')),
                'contact_us_url': urls.domestic.CONTACT_US,
            },
        )

    def clean_email(self):
        value = super().clean_email()
        if EmailAddress.objects.filter(email__iexact=value).exists():
            self.notify_already_registered(email=value)
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
    """A temporary rate limiting mechanism is implemented until the featurue is present in a
    future release of django-allauth.

    https://github.com/pennersr/django-allauth/pull/2631
    """

    TIMEOUT = 60 * 5  # restrict to only allow sending one email every 5 minutes

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

    def _get_timeout_cache_key(self, value):
        key = hashlib.sha256(value.encode('utf8')).hexdigest()
        return 'allauth/{action}:{email}'.format(action=self.__class__.__name__, email=key)

    def timeout_status(self, value):
        return cache.get(self._get_timeout_cache_key(value))

    def timeout_apply(self, value):
        duration = self.TIMEOUT
        cache.set(
            self._get_timeout_cache_key(value),
            (timezone.now() + timezone.timedelta(seconds=duration)),
            duration,
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
        # form is not valid if sent within duration set on TIMEOUT
        if self.timeout_status(email):
            raise ValidationError('Please wait before trying again.')
        return self.cleaned_data["email"]

    def save(self, request, **kwargs):
        ret = super().save(request=request, **kwargs)
        self.timeout_apply(self.cleaned_data['email'])
        return ret


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
