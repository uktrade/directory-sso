import urllib

from django.db import IntegrityError
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import RedirectView

from allauth.account import views as allauth_views
from allauth.account.views import (
    INTERNAL_RESET_URL_KEY, INTERNAL_RESET_SESSION_KEY
)
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


class DisableRegistrationMixin:

    def dispatch(self, request, *args, **kwargs):
        if settings.FEATURE_FLAGS['DISABLE_REGISTRATION_ON']:
            return redirect('https://sorry.great.gov.uk/')
        return super().dispatch(request, *args, **kwargs)


class SignupView(DisableRegistrationMixin,
                 RedirectToNextMixin,
                 allauth_views.SignupView):

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


class ConfirmEmailView(DisableRegistrationMixin, RedirectToNextMixin,
                       allauth_views.ConfirmEmailView):

    def get_context_data(self, **kwargs):
        if self.object:
            kwargs['form_url'] = get_url_with_redirect(
                url=reverse('account_confirm_email', args=(self.object.key,)),
                redirect_url=self.get_redirect_url(),
            )

        return super().get_context_data(**kwargs)


class PasswordResetFromKeyView(RedirectToNextMixin,
                               allauth_views.PasswordResetFromKeyView):
    def dispatch(self, request, uidb36, key, **kwargs):
        if settings.FEATURE_FLAGS['DISABLE_REGISTRATION_ON']:
            return redirect('https://sorry.great.gov.uk/')

        internal_session = self.request.session.get(INTERNAL_RESET_SESSION_KEY)
        # This prevents a 500 in a situation when user opened a valid internal
        # session key link without the cookie set (e.g. incognito - edge case)
        if key == INTERNAL_RESET_URL_KEY and not internal_session:
            return self.render_to_response({'token_fail': True})

        response = super().dispatch(request, uidb36, key, **kwargs)

        if key != INTERNAL_RESET_URL_KEY and response.status_code == 302:
            return redirect(urllib.parse.unquote(get_url_with_redirect(
                url=response.url,
                redirect_url=self.get_redirect_url()
            )))
        return response


class PasswordResetView(DisableRegistrationMixin,
                        allauth_views.PasswordResetView):
    pass


class PasswordChangeView(DisableRegistrationMixin,
                         allauth_views.PasswordChangeView):
    pass


class SSOLandingPage(RedirectView):
    url = settings.DEFAULT_REDIRECT_URL
