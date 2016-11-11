import urllib.parse
from django.db import IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView

from allauth.account import views as allauth_views
from allauth.account.utils import complete_signup, get_request_param
import allauth.exceptions


from sso.user.utils import get_url_with_redirect, is_valid_redirect


class RedirectToNextMixin:

    redirect_field_name = settings.REDIRECT_FIELD_NAME

    def get_redirect_url(self):
        redirect_url = settings.DEFAULT_REDIRECT_URL

        redirect_param_value = get_request_param(
            self.request, self.redirect_field_name
        )
        if redirect_param_value:
            if is_valid_redirect(urllib.parse.unquote(redirect_param_value)):
                redirect_url = redirect_param_value

        return redirect_url

    get_success_url = get_redirect_url

    def get_context_data(self, **kwargs):
        context_data = super(
            RedirectToNextMixin, self
        ).get_context_data(**kwargs)

        redirect_url = self.get_redirect_url()

        if redirect_url:
            redirect_field_value = urllib.parse.unquote(redirect_url)
        else:
            redirect_field_value = None

        context_data.update({
            self.alternative_view_url_name: get_url_with_redirect(
                url=reverse(self.alternative_view_url_name),
                redirect_url=redirect_url
            ),
            "redirect_field_name": self.redirect_field_name,
            "redirect_field_value": redirect_field_value,
        })

        return context_data


class SignupView(RedirectToNextMixin, allauth_views.SignupView):
    alternative_view_url_name = "account_login"

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


class LoginView(RedirectToNextMixin, allauth_views.LoginView):
    alternative_view_url_name = "account_signup"


class LogoutView(RedirectToNextMixin, allauth_views.LogoutView):
    alternative_view_url_name = "account_login"


class PasswordResetView(
    RedirectToNextMixin, allauth_views.PasswordResetView
):
    alternative_view_url_name = "account_login"


class ConfirmEmailView(
    RedirectToNextMixin, allauth_views.ConfirmEmailView
):
    alternative_view_url_name = "account_signup"


class PasswordResetFromKeyView(
    RedirectToNextMixin,
    allauth_views.PasswordResetFromKeyView
):
    alternative_view_url_name = "account_signup"


class SSOLandingPage(RedirectView):
    url = settings.DEFAULT_REDIRECT_URL
