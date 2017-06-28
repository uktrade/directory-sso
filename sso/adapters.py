import urllib.parse

from django.conf import settings
from django.core.urlresolvers import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_request_param

from sso.user.utils import get_url_with_redirect, is_valid_redirect


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Constructs the email confirmation (activation) url.
        """
        redirect_url = settings.DEFAULT_REDIRECT_URL

        redirect_param_value = get_request_param(
            request, settings.REDIRECT_FIELD_NAME
        )
        if redirect_param_value:
            redirect_url = redirect_param_value

        email_confirmation_url = super().get_email_confirmation_url(
            request, emailconfirmation
        )

        if redirect_url:
            if is_valid_redirect(urllib.parse.unquote(redirect_url)):
                # This is to handle the case when user registered on one device
                # (e.g. desktop) and clicked 'confirm email' on another (e.g.
                # mobile) - if user is automatically logged in on confirm
                # (which will happen when clicking confirm on same machine)
                # login view will redirect to 'next', if not (when switching
                # browsers), user will have to log in and then will be
                # redirected
                login_url_with_next = get_url_with_redirect(
                    url=reverse('account_login'),
                    redirect_url=redirect_url
                )
                email_confirmation_url = get_url_with_redirect(
                    url=email_confirmation_url,
                    redirect_url=login_url_with_next
                )
        return email_confirmation_url

    def validate_unique_email(self, email):
        # Although email has to be unique, as it is user login, do not validate
        # it, so that e-mail enumeration is not possible - security requirement
        return email

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        user = super().save_user(
            request, user, form, commit=False
        )

        user.utm = request.COOKIES.get('ed_utm', {})

        if commit:
            user.save()

        return user

    def clean_email(self, email):
        """Lowercase email."""
        return email.lower()
