import pytest
from rest_framework import status

from django.core.urlresolvers import reverse


@pytest.mark.django_db
def test_get_user_by_email_with_disabled_testapi(authed_client, settings, test_api_auth_token):
    settings.TEST_API_ENABLE = False
    response = authed_client.get(
        reverse("user_by_email", kwargs={"email": "dev@example.com"}),
        {"token": test_api_auth_token}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_user_by_email_with_enabled_testapi(authed_client, test_api_auth_token):
    response = authed_client.get(
        reverse("user_by_email", kwargs={"email": "dev@example.com"}),
        {"token": test_api_auth_token}
    )
    assert response.status_code == status.HTTP_200_OK
