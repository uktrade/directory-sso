import pytest

from django.contrib.sessions.models import Session
from django.test.client import Client

from sso.user.helpers import UserCache
from sso.user.tests import factories

password = 'pass'


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user():
    user = factories.UserFactory()
    user.set_password(password)
    user.save()
    return user


@pytest.fixture
def session(user, client):
    client.login(username=user, password=password)
    user_session = client.session
    user_session['_auth_user_id'] = user.id
    user_session.save()
    return Session.objects.get(session_key=user_session._session_key)


@pytest.fixture
def another_session(session):
    return session


@pytest.mark.django_db
def test_delete_user_cache(user, session):
    session_key = session.session_key
    UserCache.set(user=user, session=session)
    assert UserCache.get(session_key=session_key) == {
        'email': user.email,
        'id': user.id,
    }
    session.delete()
    assert UserCache.get(session_key=session_key) is None


@pytest.mark.django_db
def test_logout_deletes_cache(user, session, client):
    session_key = session.session_key
    UserCache.set(user=user, session=session)
    assert UserCache.get(session_key=session_key) == {
        'email': user.email,
        'id': user.id,
    }
    client.logout()
    assert UserCache.get(session_key=session_key) is None


@pytest.mark.django_db
def test_update_user_deletes_cache(user, session, client):
    session_key = session.session_key
    UserCache.set(user=user, session=session)
    assert UserCache.get(session_key=session_key) == {
        'email': user.email,
        'id': user.id,
    }
    user.email = 'thinger@example.cpm'
    user.save()
    assert UserCache.get(session_key=session_key) is None


@pytest.mark.django_db
def test_update_user_deletes_cache_multiple_logged_in_session(
    user, session, another_session, client
):
    UserCache.set(user=user, session=session)
    UserCache.set(user=user, session=another_session)
    assert UserCache.get(session_key=session.session_key) == {
        'email': user.email,
        'id': user.id,
    }
    assert UserCache.get(session_key=another_session.session_key) == {
        'email': user.email,
        'id': user.id,
    }
    user.email = 'thinger@example.cpm'
    user.save()
    assert UserCache.get(session_key=session.session_key) is None
    assert UserCache.get(session_key=another_session.session_key) is None
