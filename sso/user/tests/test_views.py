import http

import pytest

from sso.user.models import User
from django.core.urlresolvers import reverse


@pytest.fixture
def user():
    return User.objects.create(email='test@example.com')


@pytest.fixture
def authed_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_public_views(client):
    for name in ('account_login', 'account_signup'):
        response = client.get(reverse(name))
        assert response.status_code == 200


@pytest.mark.django_db
def test_logout_ur(authed_client, settings):
    settings.LOGOUT_REDIRECT_URL = 'http://www.example.com'
    response = authed_client.post(reverse('account_logout'))
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL
    assert response.status_code == http.client.FOUND
