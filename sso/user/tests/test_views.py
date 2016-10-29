import http

from allauth.account.models import (
    EmailAddress,
    EmailConfirmationHMAC
)
import pytest

from sso.user.models import User
from django.core import mail
from django.core.urlresolvers import reverse


@pytest.fixture
def user():
    return User.objects.create_user(
        email='test@example.com',
        password='password',
    )


@pytest.fixture
def verified_user():
    user = User.objects.create_user(
        email='verified@example.com',
        password='password',
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True
    )
    return user


@pytest.fixture
def authed_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def email(user):
    return EmailAddress.objects.create(
        user=user,
        email='a@b.com',
        verified=False,
        primary=True
    )


@pytest.fixture
def email_confirmation(email):
    return EmailConfirmationHMAC(email)


@pytest.mark.django_db
def test_public_views(client):
    for name in ('account_login', 'account_signup'):
        response = client.get(reverse(name))
        assert response.status_code == 200


@pytest.mark.django_db
def test_login_redirect_default_param(client, verified_user, settings):
    settings.LOGOUT_REDIRECT_URL = 'http://www.example.com'
    response = client.post(
        reverse('account_login'),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://www.example.com'


@pytest.mark.django_db
def test_login_redirect_next_param(client, settings, verified_user):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    url = reverse('account_login')
    expected = 'http://example.com'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://example.com'


@pytest.mark.django_db
def test_logout_redirect_default_param(authed_client, settings):
    settings.LOGOUT_REDIRECT_URL = 'http://www.example.com'
    response = authed_client.post(reverse('account_logout'))

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://www.example.com'


@pytest.mark.django_db
def test_logout_redirect_next_param(authed_client, settings):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    url = reverse('account_logout')
    expected = 'http://example.com'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=expected)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://example.com'


@pytest.mark.django_db
def test_confirm_email_redirect_next_param(settings, client,
                                           email_confirmation):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    expected = 'http://www.example.com'
    signup_url = reverse('account_signup')

    # signup with `next` param and send 'confirm email' email
    client.post(
        '{url}?next={next}'.format(url=signup_url, next=expected),
        data={
            'email': 'jim@example.com',
            'password1': '0123456',
            'password2': '0123456',
        }
    )
    body = mail.outbox[0].body
    # Extract URL for `password_reset_from_key` view and access it
    url = body[body.find('/accounts/confirm-email/'):].split()[0]

    response = client.get(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_confirm_email_redirect_default_param(settings, client,
                                              email_confirmation):
    # signup with `next` param and send 'confirm email' email
    client.post(
        reverse('account_signup'),
        data={
            'email': 'jim@example.com',
            'password1': '0123456',
            'password2': '0123456',
        }
    )
    body = mail.outbox[0].body
    # Extract URL for `password_reset_from_key` view and access it
    url = body[body.find('/accounts/confirm-email/'):].split()[0]

    response = client.get(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_password_reset_redirect_default_param(settings, client, user):

    new_password = '123456'
    # submit form and send 'password reset link' email without a 'next' param
    client.post(
        reverse('account_reset_password'),
        data={'email': user.email}
    )
    body = mail.outbox[0].body
    # Extract URL for `password_reset_from_key` view and access it
    url = body[body.find('/accounts/password/reset/'):].split()[0]

    # Reset the password
    response = client.post(
        url, {'password1': new_password, 'password2': new_password}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_password_reset_redirect_next_param(settings, client, user):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    new_password = '123456'
    password_reset_url = reverse('account_reset_password')
    expected = 'http://www.example.com'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=expected),
        data={'email': user.email}
    )
    body = mail.outbox[0].body
    # Extract URL for `password_reset_from_key` view and access it
    url = body[body.find('/accounts/password/reset/'):].split()[0]

    # Reset the password
    response = client.post(
        url, {'password1': new_password, 'password2': new_password}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected
