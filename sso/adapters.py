import urllib.parse

from django.conf import settings

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
                email_confirmation_url = get_url_with_redirect(
                    url=email_confirmation_url,
                    redirect_url=redirect_url
                )
        return email_confirmation_url

    def validate_unique_email(self, email):
        # Although email has to be unique, as it is user login, do not validate
        # it, so that e-mail enumeration is not possible - security requirement
        return email
