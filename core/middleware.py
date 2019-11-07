from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class SSODisplayLoggedInCookieMiddleware:

    def process_response(self, request, response):
        cookie_value = 'false'
        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
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


class AdminPermissionCheckMiddleware(MiddlewareMixin):
    SSO_UNAUTHORISED_ACCESS_MESSAGE = (
        'This application now uses internal Single Sign On. Please email '
        'directory@digital.trade.gov.uk so that we can enable your account.'
    )

    def process_view(self, request, view_func, view_args, view_kwarg):
        if request.user is not None:
            if request.resolver_match.namespace == 'admin' or request.path_info.startswith('/admin/login'):
                if not request.user.is_staff and request.user.is_authenticated():
                    return HttpResponse(self.SSO_UNAUTHORISED_ACCESS_MESSAGE, status=401)