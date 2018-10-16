from django.http import HttpResponse

import pytest

from core import middleware


@pytest.fixture
def response_with_session_cookie(settings):
    settings.SESSION_COOKIE_NAME = 'session'
    response = HttpResponse()
    response.set_cookie(
        settings.SESSION_COOKIE_NAME,
        value='123',
        domain=settings.SESSION_COOKIE_DOMAIN,
        max_age=settings.SESSION_COOKIE_AGE,
    )
    return response


def test_sso_middleware_display_logged_in_state_installed(settings):
    expected = 'core.middleware.SSODisplayLoggedInCookieMiddleware'
    assert expected in settings.MIDDLEWARE_CLASSES


def test_multiple_session_cookies_middleware_feature_flags(
    rf, settings, response_with_session_cookie
):
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        'WHITELIST_SUBDOMAIN_SESSION_COOKIES_ON': False,
        'WILDCARD_SUBDOMAIN_SESSION_COOKIE_ON': True,
    }
    settings.SESSION_COOKIES_NAME_DOMAIN_MAPPING = {
        'session_export': '.export.great.gov.uk',
        'session_www': 'www.great.gov.uk',
        'session_trade': '.trade.great.gov.uk',
    }

    request = rf.get('/')

    middleware.MultipleSessionCookiesMiddleware().process_response(
        request=request, response=response_with_session_cookie
    )

    cookies = response_with_session_cookie.cookies
    assert len(cookies) == 1
    assert settings.SESSION_COOKIE_NAME in cookies


@pytest.mark.parametrize('wildcard_on,whitelist_on', (
    (True, True),
    (True, False),
    (False, True),
    (False, False)
))
def test_multiple_session_cookies_middleware_no_session_cookie(
    rf, settings, wildcard_on, whitelist_on
):
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        'WHITELIST_SUBDOMAIN_SESSION_COOKIES_ON': whitelist_on,
        'WILDCARD_SUBDOMAIN_SESSION_COOKIE_ON': wildcard_on,
    }

    request = rf.get('/')
    response = HttpResponse()

    middleware.MultipleSessionCookiesMiddleware().process_response(
        request=request, response=response
    )

    assert len(response.cookies) == 0


def test_multiple_session_cookies_middleware_subdomains(
    rf, settings, response_with_session_cookie
):
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        'WHITELIST_SUBDOMAIN_SESSION_COOKIES_ON': True,
        'WILDCARD_SUBDOMAIN_SESSION_COOKIE_ON': True,
    }
    settings.SESSION_COOKIES_NAME_DOMAIN_MAPPING = {
        'session_export': '.export.great.gov.uk',
        'session_www': 'www.great.gov.uk',
        'session_trade': '.trade.great.gov.uk',
    }

    request = rf.get('/')

    middleware.MultipleSessionCookiesMiddleware().process_response(
        request=request, response=response_with_session_cookie
    )

    cookies = response_with_session_cookie.cookies
    assert len(cookies) == 4
    assert cookies['session']['domain'] == settings.SESSION_COOKIE_DOMAIN
    assert cookies['session_export']['domain'] == '.export.great.gov.uk'
    assert cookies['session_www']['domain'] == 'www.great.gov.uk'
    assert cookies['session_trade']['domain'] == '.trade.great.gov.uk'

    for name in ['session_export', 'session_www', 'session_trade']:
        assert cookies[name].value == cookies['session'].value
        assert cookies[name]['expires'] == cookies['session']['expires']
        assert cookies[name]['max-age'] == cookies['session']['max-age']
        assert cookies[name]['path'] == cookies['session']['path']
        assert cookies[name]['secure'] == cookies['session']['secure']
        assert cookies[name]['httponly'] == cookies['session']['httponly']


def test_multiple_session_cookies_middleware_wildcard_disabled(
    rf, settings, response_with_session_cookie
):
    settings.FEATURE_FLAGS = {
        **settings.FEATURE_FLAGS,
        'WHITELIST_SUBDOMAIN_SESSION_COOKIES_ON': True,
        'WILDCARD_SUBDOMAIN_SESSION_COOKIE_ON': False
    }
    settings.SESSION_COOKIES_NAME_DOMAIN_MAPPING = {
        'session_export': '.export.great.gov.uk',
        'session_www': 'www.great.gov.uk',
        'session_trade': '.trade.great.gov.uk',
    }

    request = rf.get('/')

    middleware.MultipleSessionCookiesMiddleware().process_response(
        request=request, response=response_with_session_cookie
    )
    cookies = response_with_session_cookie.cookies

    assert settings.SESSION_COOKIE_NAME not in cookies
    assert len(cookies) == 3
    assert cookies['session_export']['domain'] == '.export.great.gov.uk'
    assert cookies['session_www']['domain'] == 'www.great.gov.uk'
    assert cookies['session_trade']['domain'] == '.trade.great.gov.uk'
    assert (
        cookies['session_export'].value ==
        cookies['session_export'].value ==
        cookies['session_trade'].value
    )
