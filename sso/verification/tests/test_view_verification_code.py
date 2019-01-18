import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_validation_code(api_client):
    response = api_client.post(
        reversed('api:verification-code')
    )

    assert response.status_code == status.HTTP_200_OK
