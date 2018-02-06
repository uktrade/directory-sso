import pytest
from django.core.urlresolvers import reverse
from rest_framework import status


@pytest.mark.django_db
def test_get_user_by_email_with_enabled_test_api(client, active_user):
    response = client.get(
        reverse("user_by_email", kwargs={"email": active_user.email})
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_should_get_sso_id_and_is_verified_flag_for_active_user(
        client, active_user):
    response = client.get(
        reverse("user_by_email", kwargs={"email": active_user.email}))
    assert response.data == {"is_verified": True, "sso_id": 1}


@pytest.mark.django_db
def test_should_get_sso_id_and_is_verified_flag_for_inactive_user(
        client, inactive_user):
    response = client.get(
        reverse("user_by_email", kwargs={"email": inactive_user.email})
    )
    assert response.data == {"is_verified": False, "sso_id": 2}


@pytest.mark.django_db
def test_should_get_404_for_non_existing_user(client):
    response = client.get(
        reverse("user_by_email", kwargs={"email": "non_existing@user.com"})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_should_get_404_when_email_is_not_present(client):
    response = client.get(
        reverse("user_by_email", kwargs={"email": ""})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_should_get_404_when_email_is_none(client):
    response = client.get(
        reverse("user_by_email", kwargs={"email": None})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_user_by_email_with_disabled_test_api(
        client, settings, active_user):
    settings.TEST_API_ENABLE = False
    response = client.get(
        reverse("user_by_email", kwargs={"email": active_user.email})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
