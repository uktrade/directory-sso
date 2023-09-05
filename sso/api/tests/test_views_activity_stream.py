import datetime

import mohawk
import pytest
from django.core.management import call_command
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from sso.user.tests.factories import UserFactory, UserProfileFactory

WHITELISTED_X_FORWARDED_FOR_HEADER = '1.2.3.4, ' + '4.5.5.5, ' + '3.5.5.5, ' + '2.5.5.5, ' + '1.5.5.5'


@pytest.fixture
def api_client():
    return APIClient()


def _url():
    return 'http://testserver' + reverse('api:activity-stream')


def _url_incorrect_domain():
    return 'http://incorrect' + reverse('api:activity-stream')


def _url_incorrect_path():
    return 'http://testserver' + reverse('api:activity-stream') + 'incorrect/'


def _url_activity_stream_users():
    return 'http://testserver' + reverse('api:activity-stream-users')


def _url_activity_stream_user_answers_vfm():
    return 'http://testserver' + reverse('api:activity-stream-user-answers-vfm')


def _auth_sender(key_id='some-id', secret_key='some-secret', url=_url, method='GET', content='', content_type=''):
    credentials = {
        'id': key_id,
        'key': secret_key,
        'algorithm': 'sha256',
    }
    return mohawk.Sender(
        credentials,
        url(),
        method,
        content=content,
        content_type=content_type,
    )


@pytest.mark.parametrize(
    'get_kwargs,expected_json',
    (
        (
            # If X-Forwarded-For is present
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Public network access denied'},
        ),
        (
            # Multiple X-Forwarded-For present
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4,5.6.7.8',
            ),
            {'detail': 'Public network access denied'},
        ),
        (
            # If the Authorization header isn't passed
            dict(
                content_type='',
            ),
            {'detail': 'Authentication credentials were not provided.'},
        ),
        (
            # If the Authorization header generated from an incorrect ID
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    key_id='incorrect',
                ).request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect secret
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(secret_key='incorrect').request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect domain
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    url=_url_incorrect_domain,
                ).request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect path
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    url=_url_incorrect_path,
                ).request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect method
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    method='POST',
                ).request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect
            # content-type
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    content_type='incorrect',
                ).request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from incorrect content
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    content='incorrect',
                ).request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
    ),
)
@pytest.mark.parametrize('url', (_url(), _url_activity_stream_users()))
@pytest.mark.django_db
def test_401_returned(api_client, url, get_kwargs, expected_json):
    """If the request isn't properly Hawk-authenticated, then a 401 is
    returned
    """
    response = api_client.get(
        url,
        **get_kwargs,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_json


@pytest.mark.django_db
def test_if_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = datetime.datetime.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = _auth_sender().request_header
    response = api_client.get(
        reverse('api:activity-stream'),
        content_type='',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response.json() == error


@pytest.mark.django_db
def test_empty_object_returned_with_authentication(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )

    assert response.status_code == status.HTTP_200_OK
    content = {'secret': 'content-for-pen-test'}
    assert response.json() == content

    # Just asserting that accept_response doesn't raise is a bit weak,
    # so we also assert that it raises if the header, content, or
    # content_type are incorrect
    sender.accept_response(
        response_header=response['Server-Authorization'],
        content=response.content,
        content_type=response['Content-Type'],
    )
    with pytest.raises(mohawk.exc.MacMismatch):
        sender.accept_response(
            response_header=response['Server-Authorization'] + 'incorrect',
            content=response.content,
            content_type=response['Content-Type'],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response['Server-Authorization'],
            content='incorrect',
            content_type=response['Content-Type'],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response['Server-Authorization'],
            content=response.content,
            content_type='incorrect',
        )


@pytest.mark.django_db
def test_activity_stream_list_users_endpoint(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    user_1 = UserFactory()
    UserProfileFactory(user=user_1, mobile_phone_number='824802648236868364')
    UserFactory.create_batch(4)
    sender = _auth_sender(url=_url_activity_stream_users)
    response = api_client.get(
        _url_activity_stream_users(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data['orderedItems']) == 2
    assert set(data['orderedItems'][0]['object'].keys()) == {
        'id',
        'type',
        'dit:DirectorySSO:User:hashedUuid',
        'dit:DirectorySSO:User:email',
        'dit:DirectorySSO:User:telephone',
        'dit:DirectorySSO:User:dateJoined',
        'dit:DirectorySSO:User:LastLogin'
    }
    assert data['next'] is not None
    assert data['previous'] is None

    sender = _auth_sender(url=lambda: data['next'])
    response = api_client.get(
        data['next'],
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data['orderedItems']) == 2
    assert data['next'] is not None
    assert data['previous'] is not None

    sender = _auth_sender(url=lambda: data['next'])
    response = api_client.get(
        data['next'],
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data['orderedItems']) == 1
    assert data['next'] is None
    assert data['previous'] is not None


@pytest.mark.django_db
def test_activity_stream_list_user_answers_vfm_endpoint(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    # Load some questions to associate

    call_command('loaddata', 'test_fixtures/user_vfm_tests.json')

    sender = _auth_sender(url=_url_activity_stream_user_answers_vfm)
    response = api_client.get(
        _url_activity_stream_user_answers_vfm(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert len(data['orderedItems']) == 2
    assert set(data['orderedItems'][0]['object'].keys()) == {
        'id',
        'type',
        'dit:DirectorySSO:UserAnswer:answer',
        'dit:DirectorySSO:UserAnswer:user:id',
        'dit:DirectorySSO:UserAnswer:user:hashed_uuid',
        'dit:DirectorySSO:UserAnswer:question:id',
        'dit:DirectorySSO:UserAnswer:question:title',
        'dit:DirectorySSO:UserAnswer:answer_label',
    }

    assert data['next'] is not None
    assert data['previous'] is None

    sender = _auth_sender(url=lambda: data['next'])
    response = api_client.get(
        data['next'],
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data['orderedItems']) == 2
    assert data['orderedItems'][0]['object']['dit:DirectorySSO:UserAnswer:answer_label'] == 'Somewhat disagree'
    assert data['next'] is not None
    assert data['previous'] is not None

    sender = _auth_sender(url=lambda: data['next'])
    response = api_client.get(
        data['next'],
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert len(data['orderedItems']) == 1
    assert data['orderedItems'][0]['object']['dit:DirectorySSO:UserAnswer:answer_label'] == [
        'Automotive',
        'Chemicals',
        'Energy',
    ]
    assert data['next'] is None
    assert data['previous'] is not None
