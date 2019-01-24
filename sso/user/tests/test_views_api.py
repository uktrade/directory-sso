import pytest

from django.urls import reverse

from rest_framework.test import APIClient
from sso.user import models


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_user_api(api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    response = api_client.post(
        reverse('api:create-user'),
        {'email': new_email, 'password': password},
        format='json'
    )
    assert response.status_code == 201
    assert models.User.objects.filter(email=new_email).count() == 1
