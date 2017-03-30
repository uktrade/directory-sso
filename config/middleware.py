from django.conf import settings
from datetime import datetime


def session_cookie_is_active(response):
    is_active = False

    session_cookie = response.cookies.get(settings.SESSION_COOKIE_NAME)
    if session_cookie:
        if session_cookie.get('expires'):
            session_cookie_expiry_datetime = datetime.strptime(
                session_cookie['expires'], "%a, %d-%b-%Y %H:%M:%S GMT"
            )

            if datetime.utcnow() < session_cookie_expiry_datetime:
                is_active = True
        else:
            is_active = True

    return is_active


class SSODisplayLoggedInCookieMiddleware:

    def process_response(self, request, response):
        cookie_value = 'false'

        if session_cookie_is_active(response):
            cookie_value = 'true'

        response.set_cookie(
            'sso_display_logged_in',
            value=cookie_value,
            domain=settings.SESSION_COOKIE_DOMAIN,
            max_age=settings.SESSION_COOKIE_AGE,
            secure=False,
            httponly=False
        )
        return response
