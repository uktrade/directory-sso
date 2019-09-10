import datetime

from oauth2_provider.models import AccessToken, Application
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse
from django.utils import timezone

from sso.user.models import User


def setup_data():
    superuser = User.objects.create_user(
        email='superuser@example.com',
        password='pass',
        is_superuser=True
    )
    application = Application.objects.create(
        client_id='test',
        user=superuser,
        client_type='Confidential',
        authorization_grant_type='Authorization code',
        skip_authorization=True
    )
    user = User.objects.create(
        email='test@example.com',
        password='pass'
    )
    access_token = AccessToken.objects.create(
        user=user,
        token='test',
        application=application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope='profile'
    )

    return superuser, application, user, access_token


@pytest.mark.django_db
def test_user_retrieve_view_authorised():
    _, _, user, access_token = setup_data()

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Bearer {}'.format(access_token.token)
    )

    response = client.get(reverse('oauth2_provider:user-profile'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email


@pytest.mark.django_db
def test_user_retrieve_view_no_token():
    setup_data()

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Bearer '
    )

    response = client.get(reverse('oauth2_provider:user-profile'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_retrieve_view_invalid_token():
    setup_data()

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Bearer invalid_token'
    )

    response = client.get(reverse('oauth2_provider:user-profile'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
