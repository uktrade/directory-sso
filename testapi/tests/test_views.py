import pytest
from django.core.urlresolvers import reverse
from rest_framework import status


@pytest.mark.django_db
def test_get_user_by_email_with_enabled_test_api(
        client, test_api_auth_token, active_user):
    response = client.get(
        reverse("user_by_email", kwargs={"email": active_user.email}),
        {"token": test_api_auth_token}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_should_get_sso_id_and_is_verified_flag_for_active_user(
        client, test_api_auth_token, active_user):
    response = client.get(
        reverse("user_by_email", kwargs={"email": active_user.email}),
        {"token": test_api_auth_token}
    )
    assert response.data == {"is_verified": True, "sso_id": 1}


@pytest.mark.django_db
def test_should_get_sso_id_and_is_verified_flag_for_inactive_user(
        client, test_api_auth_token, inactive_user):
    response = client.get(
        reverse("user_by_email", kwargs={"email": inactive_user.email}),
        {"token": test_api_auth_token}
    )
    assert response.data == {"is_verified": False, "sso_id": 2}


@pytest.mark.django_db
def test_should_get_404_for_non_existing_user(
        client, test_api_auth_token):
    response = client.get(
        reverse("user_by_email", kwargs={"email": "non_existing@user.com"}),
        {"token": test_api_auth_token}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_should_get_404_when_email_is_not_present(client, test_api_auth_token):
    response = client.get(
        reverse("user_by_email", kwargs={"email": ""}),
        {"token": test_api_auth_token}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_user_by_email_with_disabled_test_api(
        client, settings, test_api_auth_token, active_user):
    settings.TEST_API_ENABLE = False
    response = client.get(
        reverse("user_by_email", kwargs={"email": active_user.email}),
        {"token": test_api_auth_token}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_by_email_without_auth_token(client):
    response = client.get(
        reverse("user_by_email", kwargs={"email": "some@user.com"})
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_by_email_with_invalid_auth_token(client):
    response = client.get(
        reverse("user_by_email", kwargs={"email": "some@user.com"}),
        {"token": "invalid token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
