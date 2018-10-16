from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


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


class MultipleSessionCookiesMiddleware(SessionMiddleware):

    def process_response(self, request, response):
        # some subdomains of .great.gov.uk are hosted externally. The SSO
        # session cookie must therefore not be exposed to those untrusted
        # subdomains.
        # This is solved by creating different cookie names on the same
        # response with different values.
        # For this to work the view that sets the session cookie must be on
        # great.gov.uk (rather than a subdomain): proxy view or hosted on
        # great.gov.uk/sso
        response = super().process_response(request=request, response=response)
        if settings.SESSION_COOKIE_NAME not in response.cookies:
            return response
        if settings.FEATURE_FLAGS['WHITELIST_SUBDOMAIN_SESSION_COOKIES_ON']:
            cookie = response.cookies[settings.SESSION_COOKIE_NAME]
            mapping = settings.SESSION_COOKIES_NAME_DOMAIN_MAPPING
            for name, domain in mapping.items():
                new_cookie = cookie.copy()
                new_cookie.key = name
                new_cookie['domain'] = domain
                response.cookies[new_cookie.key] = new_cookie
        if not settings.FEATURE_FLAGS['WILDCARD_SUBDOMAIN_SESSION_COOKIE_ON']:
            del response.cookies[settings.SESSION_COOKIE_NAME]
        return response
