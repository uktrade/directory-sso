import re

from allauth.account import views

from django.conf import settings
from django.views.generic import RedirectView

from sso.adapters import validate_next
from sso import constants


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


class FeedbackView(RedirectView):
    url = constants.FEEDBACK_FORM_URL


class TermsView(RedirectView):
    url = constants.TERMS_AND_CONDITIONS_URL


class SSOLandingPage(RedirectView):
    url = settings.ROOT_REDIRECT_URL
