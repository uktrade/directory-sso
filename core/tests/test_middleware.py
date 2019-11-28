from django.http import HttpResponse

import pytest
from core.tests.test_helpers import reload_urlconf
from django.urls import reverse
from django.test.client import Client
from sso.user.tests import factories


AUTHENTICATION_BACKENDS_CLASSES = (
    'authbroker_client.backends.AuthbrokerBackend',
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)


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


@pytest.fixture(autouse=False)
def admin_user():
    admin_user = factories.UserFactory(is_staff=False)
    admin_user.save()
    return admin_user


def test_sso_middleware_display_logged_in_state_installed(settings):
    assert 'core.middleware.SSODisplayLoggedInCookieMiddleware' in settings.MIDDLEWARE


@pytest.fixture()
def admin_client_sso(db, admin_user):
    """A Django test client logged in as an admin user."""
    client = Client()
    client.login(username=admin_user.email, password=admin_user._password)
    return client


@pytest.mark.django_db
def test_admin_permission_middleware_no_user(client, settings):
    settings.AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    response = client.get(reverse('admin:login'))

    assert response.status_code == 302
    assert response.url == reverse('authbroker_client:login')


@pytest.mark.django_db
def test_admin_permission_middleware_authorised_no_staff(client, settings, admin_user):
    settings.AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    client.force_login(admin_user)

    response = client.get(reverse('admin:login'))

    assert response.status_code == 302


@pytest.mark.django_db
def test_admin_permission_middleware_authorised_with_staff(client, settings, admin_user):
    settings.AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS_CLASSES
    settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
    reload_urlconf()
    admin_user.is_staff = True
    admin_user.save()
    client.force_login(admin_user)
    response = client.get(reverse('admin:login'))

    assert response.status_code == 302
