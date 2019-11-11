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

    def is_admin_name_space(self, request):
        if request.resolver_match.namespace in ['authbroker_client', 'admin']:
            return True
        return False

    def is_authenticated_user(self, user):
        if user:
            return user.is_authenticated()
        return False

    def process_view(self, request, view_func, view_args, view_kwarg):
        # Django admin users without permission will be displayed custom message to request access
        if self.is_authenticated_user(request.user):
            if self.is_admin_name_space(request) or request.path_info.startswith('/admin/login'):
                if not request.user.is_staff:
                    return HttpResponse(self.SSO_UNAUTHORISED_ACCESS_MESSAGE, status=401)
