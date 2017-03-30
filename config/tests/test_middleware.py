from django.conf import settings


def test_SSODisplayLoggedInCookieMiddleware_installed():
    expected = 'config.middleware.SSODisplayLoggedInCookieMiddleware'
    assert expected in settings.MIDDLEWARE_CLASSES
