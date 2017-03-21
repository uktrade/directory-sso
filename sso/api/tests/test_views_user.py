from datetime import date
from unittest import mock
from unittest.mock import Mock

from django.core.urlresolvers import reverse
from django.test.client import Client

import pytest

from rest_framework import status
from rest_framework.test import APIClient

from sso.user.models import User
from sso.user.tests.factories import UserFactory


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
@mock.patch('sso.api.permissions.APIClientPermission.has_permission', Mock)
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


@pytest.mark.django_db
@mock.patch('sso.api.permissions.APIClientPermission.has_permission', Mock)
def test_get_session_user_valid_api_key_no_user():
    user, user_session = setup_data()

    client = APIClient()

    response = client.get(
        reverse('session-user'), data={"session_key": 'non-existent'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@mock.patch('sso.api.permissions.APIClientPermission.has_permission', Mock)
def test_get_last_login():
    users = UserFactory.create_batch(5)
    setup_data()  # creates active user that should not be in response
    client = APIClient()

    response = client.get(reverse('last-login'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 5
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    expected = [
        {
            'id': users[0].id,
            'last_login': users[0].last_login.strftime(date_format)
        },
        {
            'id': users[1].id,
            'last_login': users[1].last_login.strftime(date_format)
        },
        {
            'id': users[2].id,
            'last_login': users[2].last_login.strftime(date_format)
        },
        {
            'id': users[3].id,
            'last_login': users[3].last_login.strftime(date_format)
        },
        {
            'id': users[4].id,
            'last_login': users[4].last_login.strftime(date_format)
        },
    ]
    assert response.json() == expected


@pytest.mark.django_db
@mock.patch('sso.api.permissions.APIClientPermission.has_permission', Mock)
def test_get_last_login_with_params():
    user1 = UserFactory(last_login=date(2016, 12, 25))
    user2 = UserFactory(last_login=date(2017, 1, 1))
    user3 = UserFactory(last_login=date(2016, 12, 26))
    # outside of filtered params, should not be in response
    UserFactory(last_login=date(2016, 12, 24))
    UserFactory(last_login=date(2017, 1, 2))
    setup_data()  # creates active user that should not be in response
    client = APIClient()

    response = client.get(
        reverse('last-login'), {'start': '2016-12-25', 'end': '2017-01-01'}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    expected = [
        {
            'id': user1.id,
            'last_login': user1.last_login.strftime(date_format)
        },
        {
            'id': user2.id,
            'last_login': user2.last_login.strftime(date_format)
        },
        {
            'id': user3.id,
            'last_login': user3.last_login.strftime(date_format)
        },
    ]
    assert response.json() == expected


@pytest.mark.django_db
@mock.patch('sso.api.permissions.APIClientPermission.has_permission', Mock)
def test_get_last_login_with_invalid_date_params(client, settings):
    UserFactory(last_login=date(2016, 12, 25))
    UserFactory(last_login=date(2017, 1, 1))
    UserFactory(last_login=date(2016, 12, 26))
    setup_data()

    response = client.get(
        reverse('last-login'), {'start': '2016-A-25', 'end': '2017-B-01'}
    )

    format_error = (
        'Invalid date format. Expected '
        '%Y-%m-%d %H:%M:%S, %Y-%m-%d %H:%M:%S.%f, %Y-%m-%d %H:%M, %Y-%m-%d, '
        '%m/%d/%Y %H:%M:%S, %m/%d/%Y %H:%M:%S.%f, %m/%d/%Y %H:%M, %m/%d/%Y, '
        '%m/%d/%y %H:%M:%S, %m/%d/%y %H:%M:%S.%f, %m/%d/%y %H:%M, %m/%d/%y'
    )
    expected_errors = {
        'end': [format_error],
        'start': [format_error]
    }
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_errors
