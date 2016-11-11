import http

from allauth.account.models import (
    EmailAddress,
    EmailConfirmationHMAC
)
import pytest

from django.core import mail
from django.core.urlresolvers import reverse

from sso.user.models import User


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
def test_login_redirect_next_param_oauth2(
    client, settings, verified_user
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as&redirect_uri'
        '=https%3A%2F%2Fuktieig-secondary.staging.dxw.net%2Fusers%2Fauth'
        '%2Fexporting_is_great%2Fcallback&response_type=code&scope=profile'
        '&state=23947asdoih4380'
    )

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_login_redirect_default_param_if_no_next_param(
    client, verified_user, settings
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.example.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    response = client.post(
        reverse('account_login'),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://www.example.com'


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_internal(
    client, settings, verified_user
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = '/i-love-cats/'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == '/i-love-cats/'


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_valid(
    client, settings, verified_user
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = 'http://example.com'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://example.com'


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_invalid(
    client, settings, verified_user
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    url = reverse('account_login')
    next_param = 'http://example.com'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=next_param),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://www.other.com'


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_oath2(
    authed_client, settings
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_logout')
    expected = (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as&redirect_uri'
        '=https%3A%2F%2Fuktieig-secondary.staging.dxw.net%2Fusers%2Fauth'
        '%2Fexporting_is_great%2Fcallback&response_type=code&scope=profile'
        '&state=23947asdoih4380'
    )

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=expected)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_logout_redirect_default_param_if_no_next_param(
    authed_client, settings
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.example.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['http://www.example.com',
                                         'http://www.other.com']
    response = authed_client.post(reverse('account_logout'))

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://www.example.com'


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_valid(
    authed_client, settings
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_logout')
    expected = 'http://example.com'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=expected)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://example.com'


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_invalid(
    authed_client, settings
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    url = reverse('account_logout')
    next_param = 'http://example.com'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=next_param)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == 'http://www.other.com'


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_internal(
    authed_client, settings
):
    settings.LOGOUT_REDIRECT_URL = 'http://www.other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['http://www.example.com',
                                         'http://www.other.com']
    url = reverse('account_logout')
    expected = '/exporting/'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=expected)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == '/exporting/'


@pytest.mark.django_db
def test_confirm_email_redirect_next_param_if_next_param_valid(
    settings, client, email_confirmation
):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    expected = 'http://www.example.com'
    signup_url = reverse('account_signup')

    # signup with `next` param and send 'confirm email' email
    client.defaults['HTTP_REFERER'] = '{url}?next={next}'.format(
        url=signup_url, next=expected
    )
    client.post(
        signup_url,
        data={
            'email': 'jim@example.com',
            'email2': 'jim@example.com',
            'terms_agreed': True,
            'password1': '*' * 10,
            'password2': '*' * 10,
        }
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]

    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/confirm-email/'):].split()[0]

    response = client.get(url)

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_confirm_email_redirect_next_param_if_next_param_invalid(
    settings, client, email_confirmation
):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    next_param = 'http://www.example.com'
    signup_url = reverse('account_signup')

    # signup with `next` param and send 'confirm email' email
    client.defaults['HTTP_REFERER'] = '{url}?next={next}'.format(
        url=signup_url, next=next_param
    )
    client.post(
        signup_url,
        data={
            'email': 'jim@example.com',
            'email2': 'jim@example.com',
            'terms_agreed': True,
            'password1': '*' * 10,
            'password2': '*' * 10,
        }
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]

    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/confirm-email/'):].split()[0]

    response = client.get(url)

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_confirm_email_redirect_next_param_if_next_param_internal(
    settings, client, email_confirmation
):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    expected = '/exporting/'
    signup_url = reverse('account_signup')

    # signup with `next` param and send 'confirm email' email
    client.defaults['HTTP_REFERER'] = '{url}?next={next}'.format(
        url=signup_url, next=expected
    )
    client.post(
        signup_url,
        data={
            'email': 'jim@example.com',
            'email2': 'jim@example.com',
            'terms_agreed': True,
            'password1': '*' * 10,
            'password2': '*' * 10,
        }
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]

    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/confirm-email/'):].split()[0]

    response = client.get(url)

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_confirm_email_redirect_default_param_if_no_next_param(
    settings, client, email_confirmation
):

    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    client.post(
        reverse('account_signup'),
        data={
            'email': 'jim@example.com',
            'email2': 'jim@example.com',
            'terms_agreed': True,
            'password1': '*' * 10,
            'password2': '*' * 10,
        }
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]
    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/confirm-email/'):].split()[0]

    response = client.get(url)

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_password_reset_redirect_default_param_if_no_next_param(
    settings, client, user
):

    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = '*' * 10
    # submit form and send 'password reset link' email without a 'next' param
    client.post(
        reverse('account_reset_password'),
        data={'email': user.email}
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]
    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/password/reset/'):].split()[0]

    # Reset the password
    response = client.post(
        url, {'password1': new_password, 'password2': new_password}
    )
    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_valid(
    settings, client, user
):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = '*' * 10
    password_reset_url = reverse('account_reset_password')
    expected = 'http://www.example.com'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=expected),
        data={'email': user.email}
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]
    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/password/reset/'):].split()[0]

    # Reset the password
    response = client.post(
        url, {'password1': new_password, 'password2': new_password}
    )

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_invalid(
    settings, client, user
):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    new_password = '*' * 10
    password_reset_url = reverse('account_reset_password')
    next_param = 'http://www.example.com'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=next_param),
        data={'email': user.email}
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]
    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/password/reset/'):].split()[0]

    # Reset the password
    response = client.post(
        url, {'password1': new_password, 'password2': new_password}
    )

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_internal(
    settings, client, user
):
    settings.LOGOUT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = '*' * 10
    password_reset_url = reverse('account_reset_password')
    expected = '/exporting/'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=expected),
        data={'email': user.email}
    )
    message = mail.outbox[0]
    txt = message.body
    html = message.alternatives[0][0]
    # Extract URL for `password_reset_from_key` view and access it
    url = txt[txt.find('/accounts/password/reset/'):].split()[0]

    # Reset the password
    response = client.post(
        url, {'password1': new_password, 'password2': new_password}
    )

    assert url in txt
    assert url in html
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_password_reset_doesnt_allow_email_enumeration(
    settings, client, user
):

    # submit form and send 'password reset link' email without a 'next' param
    response = client.post(
        reverse('account_reset_password'),
        data={'email': 'imaginaryemail@example.com'}
    )

    # don't send an email cause no account exists
    assert len(mail.outbox) == 0
    # but redirect anyway so attackers dont find out if it exists
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('account_reset_password_done')
