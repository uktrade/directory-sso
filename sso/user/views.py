from allauth.account import views
from allauth.account.utils import get_request_param

from django.conf import settings


class LogoutView(views.LogoutView):
    def get_redirect_url(self):
        redirect_to = get_request_param(self.request, self.redirect_field_name)
        return redirect_to or settings.LOGOUT_REDIRECT_URL


class ConfirmEmailView(views.ConfirmEmailView):

    redirect_field_name = 'next'

    def get_redirect_url(self):
        redirect_to = get_request_param(self.request, self.redirect_field_name)
        return redirect_to or settings.LOGOUT_REDIRECT_URL


class PasswordResetFromKeyView(views.PasswordResetFromKeyView):

    redirect_field_name = 'next'

    def get_success_url(self):
        redirect_to = get_request_param(self.request, self.redirect_field_name)
        return redirect_to or settings.LOGOUT_REDIRECT_URL
