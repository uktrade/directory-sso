from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect


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

    def process_response(self, request, response):
        # After successful login SSO users need to go to settings.LOGIN_REDIRECT_URL
        # Django admin users need to be redirected to the admin sceeen
        if request.user is not None and not self.is_admin_page_request(response):
            if self.is_login_redirect_url(response) and self.is_admin_name_space(request):
                return HttpResponseRedirect(settings.LOGIN_ADMIN_REDIRECT_URL)
        return response

    def is_admin_name_space(self, request):
        if request.resolver_match.namespace in ['authbroker_client', 'admin']:
            return True
        return False

    def is_login_redirect_url(self, response):
        if hasattr(response, 'url'):
            if response.url == settings.LOGIN_REDIRECT_URL:
                return True
        return False

    def is_admin_page_request(self, response):
        if hasattr(response, 'template_name'):
            if response.template_name == 'admin/index.html':
                return True
        return False

    def process_view(self, request, view_func, view_args, view_kwarg):
        # Django admin users without permission will be displayed custom message to request access
        if request.user is not None:
            if request.resolver_match.namespace == 'admin' or request.path_info.startswith('/admin/login'):
                if not request.user.is_staff and request.user.is_authenticated():
                    return HttpResponse(self.SSO_UNAUTHORISED_ACCESS_MESSAGE, status=401)

    def get_success_url(self):
        return resolve_url(settings.LOGIN_ADMIN_REDIRECT_URL)
