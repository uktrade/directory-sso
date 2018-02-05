import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse

from config.settings import TEST_API_AUTH_TOKEN


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_get_user_by_email(api_client):
    response = api_client.get(
        reverse("user_by_email", kwargs={"email": "dev@example.com"}),
        {"token": TEST_API_AUTH_TOKEN}
    )
    assert response.status_code == status.HTTP_200_OK
