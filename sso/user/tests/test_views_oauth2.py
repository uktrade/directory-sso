import datetime

from django.core.urlresolvers import reverse

import pytest

from rest_framework import status
from rest_framework.test import APIClient
from oauth2_provider.models import AccessToken, Application

from sso.user.models import User


@pytest.mark.django_db
def test_user_retrieve_view():
    superuser = User.objects.create(
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
        expires=datetime.datetime.now() + datetime.timedelta(days=1),
        scope='profile'
    )

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Bearer {}'.format(access_token.token)
    )

    response = client.get(reverse('user-profile'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email
