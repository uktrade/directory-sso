from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_request_param

from sso.user.utils import get_url_with_redirect, is_valid_redirect


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Constructs the email confirmation (activation) url.
        """
        redirect_url = get_request_param(
            request, settings.REDIRECT_FIELD_NAME
        )

        email_confirmation_url = super().get_email_confirmation_url(
            request, emailconfirmation
        )

        if redirect_url and is_valid_redirect(redirect_url):
            email_confirmation_url = get_url_with_redirect(
                url=email_confirmation_url,
                redirect_url=redirect_url
            )
        return email_confirmation_url

    def validate_unique_email(self, email):
        # Although email has to be unique, as it is user login, do not validate
        # it, so that e-mail enumeration is not possible - security requirement
        return email
