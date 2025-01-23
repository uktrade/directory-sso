import os

import pytest
from dbt_copilot_python.utility import is_copilot
from django.http import HttpResponse
from django.test.client import Client
from django.urls import reverse

from core.tests.test_helpers import reload_urlconf
from sso.user.tests import factories

AUTHENTICATION_BACKENDS_CLASSES = (
    'authbroker_client.backends.AuthbrokerBackend',
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
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


@pytest.mark.django_db
def test_x_forward_for_middleware_with_expected_ip(client, settings):
    os.environ["COPILOT_ENVIRONMENT_NAME"] = "dev"
    settings.ALLOWED_IPS = ['1.2.3.4', '123.123.123.123']
    reload_urlconf()

    # Middleware is for DBT only and should only trigger is is_copilot() is true
    assert is_copilot() is True

    response = client.get(
        reverse('pingdom'),
        content_type='',
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == 200
    os.environ.pop("COPILOT_ENVIRONMENT_NAME")


@pytest.mark.django_db
def test_x_forward_for_middleware_with_unexpected_ip(client, settings):
    os.environ["COPILOT_ENVIRONMENT_NAME"] = "dev"
    settings.ALLOWED_IPS = [
        '0.0.0.0',
    ]
    reload_urlconf()

    # Middleware is for DBT only and should only trigger is is_copilot() is true
    assert is_copilot() is True

    response = client.get(
        reverse('pingdom'),
        content_type='',
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == 401
    os.environ.pop("COPILOT_ENVIRONMENT_NAME")

