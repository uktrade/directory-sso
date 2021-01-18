import pytest
from django.test.client import Client
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core import authentication
from sso.user.tests.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def valid_session(user):
    client = Client()
    session = client.session
    session['_auth_user_id'] = user.id
    session.save()
    return session


@pytest.fixture
def expired_session(user):
    client = Client()
    session = client.session
    session['_auth_user_id'] = user.id
    session.set_expiry(-1)
    session.save()
    return session


class TestView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response()


@pytest.mark.django_db
def test_sso_session_authentication_invalid_header(rf):
    request = rf.get('/', HTTP_AUTHORIZATION='SSO_SESSION_ID')
    response = TestView.as_view()(request)

    assert response.status_code == 401
    assert response.render().content == (b'{"detail":"Invalid SSO_SESSION_ID header."}')


@pytest.mark.django_db
def test_sso_session_authentication_valid_session_key(valid_session, rf):
    request = rf.get('/', HTTP_AUTHORIZATION=f'SSO_SESSION_ID {valid_session._session_key}')
    response = TestView.as_view()(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_sso_session_authentication_expired_session(expired_session, rf):
    request = rf.get('/', HTTP_AUTHORIZATION=f'SSO_SESSION_ID {expired_session._session_key}')
    response = TestView.as_view()(request)

    assert response.status_code == 401
    assert response.render().content == b'{"detail":"Invalid session id"}'


@pytest.mark.django_db
def test_sso_session_authentication_no_user(rf):
    request = rf.get('/', HTTP_AUTHORIZATION='SSO_SESSION_ID not-exist')
    response = TestView.as_view()(request)

    assert response.status_code == 401
    assert response.render().content == b'{"detail":"Invalid session id"}'
