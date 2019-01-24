import pytest
from unittest.mock import patch

from django.urls import reverse

from rest_framework.test import APIClient
from sso.user.models import User
from sso.verification.models import VerificationCode
from sso.user.serializers import CreateUserSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_user_api(api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    response = api_client.post(
        reverse('api:user'),
        {'email': new_email, 'password': password},
        format='json'
    )
    assert response.status_code == 201
    assert User.objects.filter(email=new_email).count() == 1


@pytest.mark.django_db
@patch('sso.user.models.User.objects.create_user')
def test_create_user_api_exception_rollback(mock_create, api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        response = api_client.post(
            reverse('api:user'),
            {'email': new_email, 'password': password},
            format='json'
        )
        assert response.status_code == 500
    assert User.objects.count() == 0
    assert VerificationCode.objects.count() == 0
