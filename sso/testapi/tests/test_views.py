import json

import pytest
from django.urls import reverse
from rest_framework import status

from sso.testapi.conftest import AutomatedTestUserFactory


@pytest.mark.django_db
def test_get_user_by_email_with_enabled_test_api(client, active_user):
    response = client.get(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email})
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_should_get_sso_id_and_is_verified_flag_for_active_user(
        client, active_user):
    response = client.get(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email}))
    assert response.data == {'is_verified': True, 'sso_id': 11}


@pytest.mark.django_db
def test_should_get_sso_id_and_is_verified_flag_for_inactive_user(
        client, inactive_user):
    response = client.get(
        reverse('testapi:user_by_email', kwargs={'email': inactive_user.email})
    )
    assert response.data == {'is_verified': False, 'sso_id': 22}


@pytest.mark.django_db
def test_should_get_404_for_non_existing_user(client):
    kwargs = {'email': 'non_existing@user.com'}
    response = client.get(
        reverse('testapi:user_by_email', kwargs=kwargs)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_should_get_404_when_email_is_not_present(client):
    response = client.get(
        reverse('testapi:user_by_email', kwargs={'email': ''})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_should_get_404_when_email_is_none(client):
    response = client.get(
        reverse('testapi:user_by_email', kwargs={'email': None})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_user_by_email_with_disabled_test_api(
        client, settings, active_user):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'TEST_API_ON': False}
    response = client.get(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_user_by_email_with_enabled_test_api(client, active_user):
    response = client.delete(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email})
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_non_existing_user_should_get_404(client):
    kwargs = {'email': 'non_existing@user.com'}
    response = client.delete(
        reverse('testapi:user_by_email', kwargs=kwargs)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_user_should_get_404_when_email_is_not_present(client):
    response = client.delete(
        reverse('testapi:user_by_email', kwargs={'email': ''})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_user_should_get_404_when_email_is_none(client):
    response = client.delete(
        reverse('testapi:user_by_email', kwargs={'email': None})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_user_by_email_with_disabled_test_api(
        client, settings, active_user):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'TEST_API_ON': False}
    response = client.delete(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email})
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize('data', [
    {'is_verified': True},
    {'is_verified': False},
])
@pytest.mark.django_db
def test_patch_user_by_email_with_enabled_test_api(client, active_user, data):
    response = client.patch(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email}),
        data=json.dumps(data), content_type='application/json'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.parametrize('data', [
    {'is_verified': True},
    {'is_verified': False},
])
@pytest.mark.django_db
def test_patch_non_existing_user_should_get_404(client, data):
    kwargs = {'email': 'non_existing@user.com'}
    response = client.patch(
        reverse('testapi:user_by_email', kwargs=kwargs),
        data=data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize('data', [
    {'is_verified': True},
    {'is_verified': False},
])
@pytest.mark.django_db
def test_patch_user_should_get_404_when_email_is_not_present(client, data):
    response = client.patch(
        reverse('testapi:user_by_email', kwargs={'email': ''}),
        data=data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize('data', [
    {'is_verified': True},
    {'is_verified': False},
])
@pytest.mark.django_db
def test_patch_user_should_get_404_when_email_is_none(client, data):
    response = client.patch(
        reverse('testapi:user_by_email', kwargs={'email': None}),
        data=data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize('data', [
    {'is_verified': True},
    {'is_verified': False},
])
@pytest.mark.django_db
def test_patch_user_by_email_with_disabled_test_api(
        client, settings, active_user, data):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'TEST_API_ON': False}
    response = client.patch(
        reverse('testapi:user_by_email', kwargs={'email': active_user.email}),
        data=data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_test_users(client):
    AutomatedTestUserFactory.create_batch(3)
    response = client.delete(reverse('testapi:test_users'))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_test_users_returns_404_when_no_test_users(client):
    response = client.delete(reverse('testapi:test_users'))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_test_users_returns_404_with_disabled_testapi(client, settings):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'TEST_API_ON': False}
    AutomatedTestUserFactory.create()
    response = client.delete(reverse('testapi:test_users'))
    assert response.status_code == status.HTTP_404_NOT_FOUND
