from dbt_copilot_python.utility import is_copilot
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SSODisplayLoggedInCookieMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        cookie_value = 'false'
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            cookie_value = 'true'
        response.set_cookie(
            'sso_display_logged_in',
            value=cookie_value,
            domain=settings.SESSION_COOKIE_DOMAIN,
            max_age=settings.SESSION_COOKIE_AGE,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=False,
        )
        return response


class AdminPermissionCheckMiddleware(MiddlewareMixin):
    SSO_UNAUTHORISED_ACCESS_MESSAGE = (
        'This application now uses internal Single Sign On. Please email '
        'directory@digital.trade.gov.uk so that we can enable your account.'
    )

    def is_admin_name_space(self, request):
        if request.resolver_match.namespace in ['authbroker_client', 'admin']:
            return True
        return False

    def process_view(self, request, view_func, view_args, view_kwarg):
        # Django admin users without permission will be displayed custom message to request access
        if request.user.is_authenticated:
            if self.is_admin_name_space(request) or request.path_info.startswith('/admin/login'):
                if not request.user.is_staff:
                    return HttpResponse(self.SSO_UNAUTHORISED_ACCESS_MESSAGE, status=401)


class XForwardForCheckMiddleware(MiddlewareMixin):
    CLIENT_IP_ERROR_MESSAGE = 'X Forward For checks failed'

    def process_request(self, request):
        if is_copilot():
            # 200 response if client IP from x-forwarded-for header in ALLOWED_IPS, else 401.
            try:
                client_ips = request.META['HTTP_X_FORWARDED_FOR'].split(',')
                for ip in client_ips:
                    if ip.strip() not in settings.ALLOWED_IPS:
                        return HttpResponse(self.CLIENT_IP_ERROR_MESSAGE, status=401)
            except (IndexError, KeyError):
                return HttpResponse(self.CLIENT_IP_ERROR_MESSAGE, status=401)
