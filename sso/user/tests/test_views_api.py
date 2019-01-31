import pytest
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APIClient

from sso.user.tests.factories import UserFactory
from sso.user.models import User, UserProfile
from sso.verification.models import VerificationCode


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
    data = response.json()
    assert data['email'] == new_email
    assert data['verification_code']


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


@pytest.mark.django_db
@patch('sso.verification.models.VerificationCode.objects.create')
def test_create_user_api_verification_exception_rollback(
        mock_create, api_client):
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


@pytest.mark.django_db
def test_create_user_profile(api_client):
    user = UserFactory()
    data = {'first_name': 'john',
            'last_name': 'smith',
            'mobile_phone_number': '0203044213',
            'job_title': 'Director',
            }

    assert UserProfile.objects.filter(user=user).count() == 0
    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api:user-create-profile'),
        data,
        format='json'
    )

    instance = UserProfile.objects.last()
    assert response.status_code == 201
    assert instance.first_name == data['first_name']
    assert instance.last_name == data['last_name']
    assert instance.job_title == data['job_title']
    assert instance.mobile_phone_number == data['mobile_phone_number']


@pytest.mark.django_db
def test_create_user_profile_no_auth(api_client):
    response = api_client.post(
        reverse('api:user-create-profile'),
        {},
        format='json'
    )
    assert response.status_code == 401
