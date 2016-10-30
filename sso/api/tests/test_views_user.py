from django.core.urlresolvers import reverse
from django.test.client import Client

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from sso.user.models import User


def setup_data():
    user = User.objects.create_user(
        email='user@example.com',
        password='pass',
    )
    client = Client()
    client.login(username='admin', password='admin')
    user_session = client.session
    user_session['_auth_user_id'] = user.id
    user_session.save()

    return user, user_session


@pytest.mark.django_db
def test_get_session_user_valid_api_key():
    user, user_session = setup_data()

    client = APIClient()

    response = client.get(
        reverse('session-user'),
        data={"session_key": user_session._session_key},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email
    assert response.data['id'] == user.id
