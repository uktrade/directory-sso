import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application
from rest_framework import status
from rest_framework.test import APIClient

from sso.user.models import User, UserProfile
from sso.oauth2.tests import factories


def setup_data():
    superuser = User.objects.create_user(email='superuser@example.com', password='pass', is_superuser=True)
    application = Application.objects.create(
        client_id='test',
        user=superuser,
        client_type='Confidential',
        authorization_grant_type='Authorization code',
        skip_authorization=True,
    )
    user = User.objects.create(email='test@example.com', password='pass')
    user_profile = UserProfile.objects.create(
        first_name='alexander',
        last_name='thegreatdotgovdotuk',
        mobile_phone_number='0203044213',
        job_title='Director',
        user=user,
    )
    access_token = AccessToken.objects.create(
        user=user,
        token='test',
        application=application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope='profile',
    )

    return superuser, application, user, user_profile, access_token


@pytest.fixture
def user_fixture():
    return factories.UserFactory.create(email='test_fixture@example.com')


@pytest.fixture
def access_token_fixture(user_fixture):
    return factories.AccessTokenFactory.create(user=user_fixture)


@pytest.mark.django_db
def test_user_retrieve_view_authorised():
    _, _, user, user_profile, access_token = setup_data()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(access_token.token))

    response = client.get(reverse('oauth2_provider:user-profile'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email
    assert response.data['user_profile']['first_name'] == user_profile.first_name
    assert response.data['user_profile']['last_name'] == user_profile.last_name


@pytest.mark.django_db
def test_user_retrieve_view_no_token():
    setup_data()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ')

    response = client.get(reverse('oauth2_provider:user-profile'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_retrieve_view_invalid_token():
    setup_data()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')

    response = client.get(reverse('oauth2_provider:user-profile'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
