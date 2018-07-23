from datetime import date, timedelta
from unittest.mock import patch, Mock

from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.core.urlresolvers import reverse
from django.test.client import Client

from sso.user.models import User
from sso.user.tests.factories import UserFactory
from sso.user.helpers import UserCache


def setup_data(email='user@example.com'):
    user = User.objects.create_user(
        email=email,
        password='pass',
    )
    client = Client()
    client.login(username='admin', password='admin')
    user_session = client.session
    user_session['_auth_user_id'] = user.id
    user_session.save()

    return user, user_session


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_get_session_user_valid_session_key(api_client):
    user, user_session = setup_data()

    response = api_client.get(
        reverse('session-user'),
        data={"session_key": user_session._session_key},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user.email
    assert response.data['id'] == user.id


@pytest.mark.django_db
@patch('conf.signature.SignatureCheckPermission.has_permission', Mock)
def test_get_session_user_expired(api_client):
    user, user_session = setup_data()
    user_session.set_expiry(-1)
    user_session.save()

    response = api_client.get(
        reverse('session-user'),
        data={"session_key": user_session._session_key},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_session_user_valid_session_key_no_user(api_client):
    user, user_session = setup_data()

    response = api_client.get(
        reverse('session-user'), data={"session_key": 'non-existent'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@patch('conf.signature.SignatureCheckPermission.has_permission', Mock)
@patch.object(UserCache, 'set', wraps=UserCache.set)
def test_get_session_user_cached_response(mock_set, settings, api_client):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'USER_CACHE_ON': True}

    user, user_session = setup_data()

    response_one = api_client.get(
        reverse('session-user'),
        data={"session_key": user_session._session_key},
    )
    response_two = api_client.get(
        reverse('session-user'),
        data={"session_key": user_session._session_key},
    )

    for response in [response_one, response_two]:
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['id'] == user.id

    assert mock_set.call_count == 1


@pytest.mark.django_db
@patch.object(UserCache, 'set', wraps=UserCache.set)
def test_get_session_user_cached_response_expires(
    mock_set, settings, api_client
):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'USER_CACHE_ON': True}

    user, user_session = setup_data()

    response_one = api_client.get(
        reverse('session-user'),
        data={"session_key": user_session._session_key},
    )

    assert response_one.status_code == status.HTTP_200_OK
    assert response_one.data['email'] == user.email
    assert response_one.data['id'] == user.id

    assert mock_set.call_count == 1

    assert UserCache.get(user_session._session_key) == {
        'email': user.email,
        'id': user.id,
    }

    with freeze_time(user_session.get_expiry_date() + timedelta(seconds=1)):
        response_two = api_client.get(
            reverse('session-user'),
            data={"session_key": user_session._session_key},
        )
        assert response_two.status_code == status.HTTP_404_NOT_FOUND

    assert mock_set.call_count == 1
    assert UserCache.get(user_session._session_key) is None


@pytest.mark.django_db
@patch('conf.signature.SignatureCheckPermission.has_permission', Mock)
@patch.object(UserCache, 'set', wraps=UserCache.set)
def test_get_session_user_cached_response_multiple_users(
    mock_set, settings, api_client
):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'USER_CACHE_ON': True}

    user_session_groups = [
        setup_data(email='user@one.com'),
        setup_data(email='user@two.com'),
        setup_data(email='user@three.com'),
    ]

    # when multiple request for multiple users are made
    for user, session in (user_session_groups * 2):
        response = api_client.get(
            reverse('session-user'),
            data={"session_key": session._session_key},
        )
        # then the expected response is returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['id'] == user.id

    # but the number of unique requests is only three
    assert mock_set.call_count == 3


@pytest.mark.django_db
def test_get_last_login(api_client):
    users = UserFactory.create_batch(5)
    setup_data()  # creates active user that should not be in response

    response = api_client.get(reverse('last-login'))

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
def test_get_last_login_with_params(api_client):
    user1 = UserFactory(last_login=date(2016, 12, 25))
    user2 = UserFactory(last_login=date(2017, 1, 1))
    user3 = UserFactory(last_login=date(2016, 12, 26))
    # outside of filtered params, should not be in response
    UserFactory(last_login=date(2016, 12, 24))
    UserFactory(last_login=date(2017, 1, 2))
    setup_data()  # creates active user that should not be in response

    response = api_client.get(
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
def test_get_last_login_with_invalid_date_params(client):
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


@pytest.mark.django_db
def test_check_password_user_valid_data(api_client):
    user, user_session = setup_data()

    response = api_client.post(
        reverse('password-check'),
        data={'session_key': user_session._session_key, 'password': 'pass'},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_check_password_user_invalid_password(api_client):
    user, user_session = setup_data()

    response = api_client.post(
        reverse('password-check'),
        data={'session_key': user_session._session_key, 'password': '!!!'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_check_password_expired(api_client):
    user, user_session = setup_data()
    user_session.set_expiry(-1)
    user_session.save()

    response = api_client.post(
        reverse('password-check'),
        data={'session_key': user_session._session_key, 'password': 'pass'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_check_password_valid_session_key_no_user(api_client):
    user, user_session = setup_data()

    response = api_client.post(
        reverse('password-check'),
        data={'session_key': 'non-existent', 'password': 'pass'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
