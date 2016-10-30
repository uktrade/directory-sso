from allauth.account import views
from allauth.account.utils import get_request_param

from django.conf import settings


class RedirectToNextOrDefaultMixin:

    redirect_field_name = settings.REDIRECT_FIELD_NAME

    def get_redirect_url(self):
        redirect_to = get_request_param(self.request, self.redirect_field_name)
        return redirect_to or settings.LOGOUT_REDIRECT_URL

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
