from django.db import IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView

from allauth.account import views as allauth_views
from allauth.account.utils import complete_signup
import allauth.exceptions

from sso.user.utils import get_redirect_url, get_url_with_redirect


class RedirectToNextMixin:

    redirect_field_name = settings.REDIRECT_FIELD_NAME

    def get_redirect_url(self):
        return get_redirect_url(
            request=self.request,
            redirect_field_name=self.redirect_field_name
        )

    get_success_url = get_redirect_url


class SignupView(RedirectToNextMixin, allauth_views.SignupView):

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
    pass


class LogoutView(RedirectToNextMixin, allauth_views.LogoutView):
    pass


class ConfirmEmailView(RedirectToNextMixin, allauth_views.ConfirmEmailView):

    def get_context_data(self, **kwargs):
        if self.object:
            kwargs['form_url'] = get_url_with_redirect(
                url=reverse('account_confirm_email', args=(self.object.key,)),
                redirect_url=self.get_redirect_url(),
            )

        return super().get_context_data(**kwargs)


class PasswordResetFromKeyView(
    RedirectToNextMixin, allauth_views.PasswordResetFromKeyView
):
    pass


class SSOLandingPage(RedirectView):
    url = settings.DEFAULT_REDIRECT_URL
