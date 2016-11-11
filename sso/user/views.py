import re

from django.db import IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView

from allauth.account import views
from allauth.account.utils import complete_signup
import allauth.exceptions

from sso.adapters import validate_next


class RedirectToNextOrDefaultMixin:

    redirect_field_name = settings.REDIRECT_FIELD_NAME

    def get_next_with_params(self, request_path):
        """"Returns the URL path after 'next', including params of 'next' """
        next_pattern = re.compile(
            r'.*?\?' + self.redirect_field_name + r'\=(.*)'
        )

        match = next_pattern.match(request_path)

        if match:
            return match.groups()[0]

    def get_redirect_url(self):
        next_with_params = self.get_next_with_params(
            request_path=self.request.get_full_path()
        )

        if next_with_params and validate_next(next_with_params):
            return next_with_params

        return settings.LOGOUT_REDIRECT_URL

    get_success_url = get_redirect_url


class SignupView(views.SignupView):

    @staticmethod
    def is_email_not_unique_error(integrity_error):
        email_not_unique_message = (
            'duplicate key value violates unique '
            'constraint "user_user_email_key"'
        )
        return any((
            email_not_unique_message in arg for arg in integrity_error.args
        ))

    def form_valid(self, form):
        try:
            self.user = form.save(self.request)
        except IntegrityError as exc:
            # To prevent enumeration of users we return a fake success response
            if self.is_email_not_unique_error(exc):
                return HttpResponseRedirect(
                    reverse('account_email_verification_sent')
                )
            else:
                raise
        else:
            try:
                return complete_signup(
                    request=self.request,
                    user=self.user,
                    email_verification=settings.ACCOUNT_EMAIL_VERIFICATION,
                    success_url=self.get_success_url()
                )
            except allauth.exceptions.ImmediateHttpResponse as exc:
                return exc.response


class ConfirmEmailView(RedirectToNextOrDefaultMixin, views.ConfirmEmailView):
    pass


class LogoutView(RedirectToNextOrDefaultMixin, views.LogoutView):
    pass


class PasswordResetFromKeyView(RedirectToNextOrDefaultMixin,
                               views.PasswordResetFromKeyView):
    pass


class LoginView(RedirectToNextOrDefaultMixin,
                views.LoginView):
    pass


class SSOLandingPage(RedirectView):
    url = settings.ROOT_REDIRECT_URL
