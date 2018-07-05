def test_SSODisplayLoggedInCookieMiddleware_installed(settings):
    expected = 'core.middleware.SSODisplayLoggedInCookieMiddleware'
    assert expected in settings.MIDDLEWARE_CLASSES
