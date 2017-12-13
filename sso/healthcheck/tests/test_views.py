import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.conf import settings
from django.core.urlresolvers import reverse


def test_health_check_no_token(client):
    response = client.get(reverse('health-check'))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_health_check_valid_token(client):
    response = client.get(
        reverse('health-check'),
        {'token': settings.HEALTH_CHECK_TOKEN}
    )

    assert response.status_code == status.HTTP_200_OK

