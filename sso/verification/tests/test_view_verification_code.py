import pytest

from django.core.urlresolvers import reverse
from django.test.client import Client
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from sso.user.models import User


def setup_data(email='user@example.com'):
    user = User.objects.create_user(
        email=email,
        password='pass',
    )
    client = Client()
    client.login(username='admin', password='admin')
    user_session = client.session
    user_session['_auth_user_id'] = user.id
    user_session.save()

    return user, user_session


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.mark.django_db
def test_create_validation_code_no_auth(api_client):
    response = api_client.post(
        reverse('api:verification-code'),
        data={}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_validation_code(api_client):
    user, user_session = setup_data()
    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api:verification-code'),
    )
    assert response.status_code == status.HTTP_201_CREATED
