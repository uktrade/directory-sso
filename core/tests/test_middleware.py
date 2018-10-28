from django.http import HttpResponse

import pytest


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
