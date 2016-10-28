from allauth.account import views

from django.conf import settings


class LogoutView(views.LogoutView):
    def get_redirect_url(self):
        return settings.LOGOUT_REDIRECT_URL
