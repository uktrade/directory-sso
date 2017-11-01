from django.core.urlresolvers import reverse

from unittest.mock import patch, Mock

from rest_framework import status
from rest_framework.test import APIClient


@patch(
    'config.signature.SignatureCheckPermission.has_permission',
    Mock(return_value=True)
)
def test_health_check_has_permission():
    client = APIClient()
    response = client.get(reverse('health-check'))

    assert response.status_code == status.HTTP_200_OK

    response_data = response.data
    assert response_data['status_code'] == status.HTTP_200_OK
    assert response_data['detail'] == 'Hello world'


@patch(
    'config.signature.SignatureCheckPermission.has_permission',
    Mock(return_value=False)
)
def test_health_check_does_not_have_permission():
    client = APIClient()
    response = client.get(reverse('health-check'))

    assert response.status_code == status.HTTP_403_FORBIDDEN
