import pytest

from django.core.urlresolvers import reverse
from django.test.client import Client
from rest_framework import status
from rest_framework.test import APIClient

from sso.user.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_validation_code_no_auth(api_client):
    response = api_client.post(
        reverse('api:verification-code'),
        format='json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_validation_code(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api:verification-code'),
        format='json'
    )
    assert response.status_code == status.HTTP_201_CREATED
