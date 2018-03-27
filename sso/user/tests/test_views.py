from unittest import mock
from unittest.mock import patch
import urllib.parse
import http
from http.cookies import SimpleCookie

from django.core import mail
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy

from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.exceptions import ImmediateHttpResponse
import pytest

from sso.adapters import EMAIL_CONFIRMATION_TEMPLATE_ID, \
    PASSWORD_RESET_TEMPLATE_ID
from sso.user import models, views


@pytest.fixture
def user():
    return models.User.objects.create_user(
        email='test@example.com',
        password='password',
    )


@pytest.fixture
def verified_user():
    user = models.User.objects.create_user(
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
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    redirect_field_value = (
        '/oauth2/authorize/%3Fclient_id%3Daisudhgfg943287895as'
        '%26redirect_uri%3Dhttps%253A%252F%252Fuktieig-secondary'
        '.staging.dxw.net%252Fusers%252Fauth%252Fexporting_is_great'
        '%252Fcallback%26response_type%3Dcode%26scope%3Dprofile%26st'
        'ate%3D23947asdoih4380'
    )

    response = client.post(
        '{url}?next={next}'.format(url=url, next=redirect_field_value),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as'
        '&redirect_uri=https%3A%2F%2Fuktieig-secondary.staging.'
        'dxw.net%2Fusers%2Fauth%2Fexporting_is_great%2Fcallback&'
        'response_type=code&scope=profile&state=23947asdoih4380'
    )


@pytest.mark.django_db
def test_login_redirect_default_param_if_no_next_param(
    client, verified_user, settings
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.example.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    response = client.post(
        reverse('account_login'),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_internal(
    client, settings, verified_user
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = '/i-love-cats/'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_valid(
    client, settings, verified_user
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = 'http://example.com/?param=test'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_invalid(
    client, settings, verified_user
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    url = reverse('account_login')
    next_param = 'http://example.com'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=next_param),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_oath2(
    authed_client, settings
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_logout')
    redirect_field_value = (
        '/oauth2/authorize/%3Fclient_id%3Daisudhgfg943287895as'
        '%26redirect_uri%3Dhttps%253A%252F%252Fuktieig-secondary'
        '.staging.dxw.net%252Fusers%252Fauth%252Fexporting_is_great'
        '%252Fcallback%26response_type%3Dcode%26scope%3Dprofile%26st'
        'ate%3D23947asdoih4380'
    )

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=redirect_field_value)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as'
        '&redirect_uri=https%3A%2F%2Fuktieig-secondary.staging.'
        'dxw.net%2Fusers%2Fauth%2Fexporting_is_great%2Fcallback&'
        'response_type=code&scope=profile&state=23947asdoih4380'
    )


@pytest.mark.django_db
def test_logout_redirect_default_param_if_no_next_param(
    authed_client, settings
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.example.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['http://www.example.com',
                                         'http://www.other.com']
    response = authed_client.post(reverse('account_logout'))

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_valid(
    authed_client, settings
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_logout')
    expected = 'http://example.com/?param=test'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=expected)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_invalid(
    authed_client, settings
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    url = reverse('account_logout')
    next_param = 'http://example.com'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=next_param)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_internal(
    authed_client, settings
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['http://www.example.com',
                                         'http://www.other.com']
    url = reverse('account_logout')
    expected = '/exporting/'

    response = authed_client.post(
        '{url}?next={next}'.format(url=url, next=expected)
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@pytest.mark.django_db
def test_confirm_email_invalid_key(
    settings, client, email_confirmation
):
    response = client.get(
        '/accounts/confirm-email/invalid/'
    )

    assert response.status_code == http.client.OK
    assert "confirmation link expired or is invalid" in str(response.content)


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_redirect_next_param_if_next_param_valid(
    mocked_notification_client, settings, client, email_confirmation
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    expected = 'http://www.example.com'
    signup_url = '{url}?next={next}'.format(
        url=reverse('account_signup'), next=urllib.parse.quote(expected)
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

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )

    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)

    assert response.status_code == http.client.FOUND
    next_url = response.get('Location')

    assert next_url == (
        '/accounts/login/?next=http%3A%2F%2Fwww.example.com'
    )

    response = client.get(next_url)
    assert response.get('Location') == expected


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_redirect_next_param_if_next_param_invalid(
    mocked_notification_client, settings, client, email_confirmation
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    next_param = 'http://www.notallowed.com'
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

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )

    url = call[1]['personalisation']['confirmation_link']

    response = client.post(url)

    assert response.status_code == http.client.FOUND

    next_url = response.get('Location')

    assert next_url == (
        '/accounts/login/?next=http%3A%2F%2Fother.com'
    )

    response = client.get(next_url)
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_redirect_next_param_if_next_param_internal(
    mocked_notification_client, settings, client, email_confirmation
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    expected = '/exporting/'
    signup_url = reverse('account_signup') + "?next={}".format(expected)

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
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )

    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)

    assert response.status_code == http.client.FOUND

    next_url = response.get('Location')

    assert next_url == '/accounts/login/?next=%2Fexporting%2F'

    response = client.get(next_url)
    assert response.get('Location') == expected


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_redirect_default_param_if_no_next_param(
    mocked_notification_client, settings, client, email_confirmation
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
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )

    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_default_param_if_no_next_param(
    mocked_notification_client, settings, client, user
):

    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = '*' * 10
    # submit form and send 'password reset link' email without a 'next' param
    client.post(
        reverse('account_reset_password'),
        data={'email': user.email}
    )
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=PASSWORD_RESET_TEMPLATE_ID
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    preflight_response = client.post(url)
    response = client.post(
        preflight_response.get('Location'),
        {'password1': new_password, 'password2': new_password}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_valid(
    mocked_notification_client, settings, client, user
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = '*' * 10
    password_reset_url = reverse('account_reset_password')
    expected = 'http://www.example.com'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=expected),
        data={'email': user.email}
    )
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=PASSWORD_RESET_TEMPLATE_ID
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    data = {
        'password1': new_password,
        'password2': new_password,
        'next': expected
    }
    preflight_response = client.post(url)
    response = client.post(
        preflight_response.get('Location'),
        data,
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_invalid(
    mocked_notification_client, settings, client, user
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    new_password = '*' * 10
    password_reset_url = reverse('account_reset_password')
    next_param = 'http://www.example.com'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=next_param),
        data={'email': user.email}
    )
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=PASSWORD_RESET_TEMPLATE_ID
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    preflight_response = client.post(url)
    response = client.post(
        preflight_response.get('Location'),
        {'password1': new_password, 'password2': new_password}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.DEFAULT_REDIRECT_URL


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_internal(
    mocked_notification_client, settings, client, user
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = '*' * 10
    password_reset_url = reverse('account_reset_password')
    expected = '/exporting/'

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=expected),
        data={'email': user.email, 'next': expected}
    )

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=PASSWORD_RESET_TEMPLATE_ID
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    preflight_response = client.post(url)
    response = client.post(
        preflight_response.get('Location'),
        {'password1': new_password, 'password2': new_password}
    )

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == expected


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_doesnt_allow_email_enumeration(
    mocked_notification_client, settings, client, user
):
    redirect_to = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    account_reset_password_url = "{}?next={}".format(
        reverse('account_reset_password'), redirect_to
    )

    data = {
        'email': 'imaginaryemail@example.com',
        'next': redirect_to
    }
    response = client.post(account_reset_password_url, data=data)

    # don't send an email cause no account exists
    assert mocked_notification_client().send_email_notification.called is False
    # but redirect anyway so attackers dont find out if it exists
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('account_reset_password_done')


@pytest.mark.django_db(transaction=True)
def test_signup_email_enumeration_not_possible(client, verified_user):
    response = client.post(
        reverse('account_signup'),
        data={
            'email': verified_user.email,
            'email2': verified_user.email,
            'terms_agreed': True,
            'password1': 'q?{7EV]V3@Z',
            'password2': 'q?{7EV]V3@Z'
        }
    )
    assert response.status_code == 302
    assert models.User.objects.all().count() == 1
    assert models.User.objects.all().last() == verified_user
    assert response.get('Location') == reverse(
        'account_email_verification_sent'
    )
    assert len(mail.outbox) == 0


@pytest.mark.django_db(transaction=True)
@patch.object(
    views, 'complete_signup',
    side_effect=ImmediateHttpResponse(response=HttpResponse(b'hello'))
)
def test_signup_email_raises_exception_allauth(mock_complete_signup, client):
    response = client.post(
        reverse('account_signup'),
        data={
            'email': 'fred@exmaple.com',
            'email2': 'fred@exmaple.com',
            'terms_agreed': True,
            'password1': 'q?{7EV]V3@Z',
            'password2': 'q?{7EV]V3@Z'
        }
    )
    assert response.content == b'hello'


@pytest.mark.django_db(transaction=True)
@patch.object(views.SignupView.form_class, 'save', side_effect=Exception())
def test_signup_email_raises_exception(mock_save, client):
    with pytest.raises(Exception):
        client.post(
            reverse('account_signup'),
            data={
                'email': 'fred@exmaple.com',
                'email2': 'fred@exmaple.com',
                'terms_agreed': True,
                'password1': 'q?{7EV]V3@Z',
                'password2': 'q?{7EV]V3@Z'
            }
        )


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_redirect_next_param_oath2(
    mocked_notification_client, settings, client, email_confirmation
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    redirect_field_value = (
        '/oauth2/authorize/%3Fclient_id%3Daisudhgfg943287895as'
        '%26redirect_uri%3Dhttps%253A%252F%252Fuktieig-secondary'
        '.staging.dxw.net%252Fusers%252Fauth%252Fexporting_is_great'
        '%252Fcallback%26response_type%3Dcode%26scope%3Dprofile%26st'
        'ate%3D23947asdoih4380'
    )
    signup_url = "{}?next={}".format(
        reverse('account_signup'), redirect_field_value
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

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )
    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)

    assert response.status_code == http.client.FOUND

    next_url = response.get('Location')

    assert next_url == (
        '/accounts/login/?next=%2Foauth2%2Fauthorize%2F%3Fclient_id'
        '%3Daisudhgfg943287895as%26redirect_uri%3Dhttps%253A%252F%252F'
        'uktieig-secondary.staging.dxw.net%252Fusers%252Fauth%252F'
        'exporting_is_great%252Fcallback%26response_type%3Dcode'
        '%26scope%3Dprofile%26state%3D23947asdoih4380'
    )

    response = client.get(next_url)
    assert response.get('Location') == (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as&redirect_uri'
        '=https%3A%2F%2Fuktieig-secondary.staging.dxw.net%2Fusers%2Fauth'
        '%2Fexporting_is_great%2Fcallback&response_type=code&scope=profile'
        '&state=23947asdoih4380'
    )


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_redirect_next_param(
    mocked_notification_client, settings, client, email_confirmation
):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    redirect_field_value = 'http%3A//www.test.example.com/register'
    signup_url = "{}?next={}".format(
        reverse('account_signup'), redirect_field_value
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
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )
    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)
    assert response.status_code == http.client.FOUND
    next_url = response.get('Location')

    assert next_url == (
        '/accounts/login/?next=http%3A%2F%2Fwww.test.example.com%2Fregister'
    )

    response = client.get(next_url)
    assert response.get('Location') == 'http://www.test.example.com/register'


@pytest.mark.django_db
def test_signup_page_login_has_next(
    client, settings, verified_user
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_signup')
    next_value = 'http://example.com/?param=test'

    response = client.get('{url}?next={next}'.format(url=url, next=next_value))

    assert response.status_code == http.client.OK

    expected_signup_url = (
        '/accounts/login/?next=http%3A%2F%2Fexample.com%2F%3Fparam%3Dtest'
    )
    assert expected_signup_url in response.rendered_content


@pytest.mark.django_db
def test_login_page_signup_has_next(
    client, settings, verified_user
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    next_value = 'http://example.com/?param=test'

    response = client.get('{url}?next={next}'.format(url=url, next=next_value))

    assert response.status_code == http.client.OK

    expected_signup_url = (
        '/accounts/signup/?next=http%3A%2F%2Fexample.com%2F%3Fparam%3Dtest'
    )
    assert expected_signup_url in response.rendered_content


@pytest.mark.django_db
def test_login_page_password_reset_has_next(
    client, settings, verified_user
):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    next_value = 'http://example.com/?param=test'

    response = client.get('{url}?next={next}'.format(url=url, next=next_value))

    assert response.status_code == http.client.OK

    expected_password_reset_url = (
        '/password/reset/?next=http%3A%2F%2Fexample.com%2F%3Fparam%3Dtest'
    )
    assert expected_password_reset_url in response.rendered_content


@patch('sso.adapters.NotificationsAPIClient', mock.Mock())
@pytest.mark.django_db
def test_signup_saves_utm(
    settings, client, email_confirmation
):

    ed_utm_cookie_value = (
        '{"utm_campaign": "whatever", "utm_content": "whatever",'
        '"utm_medium": "whatever", "utm_source": "whatever", '
        '"utm_term": "whatever"}'
    )
    client.cookies = SimpleCookie({'ed_utm': ed_utm_cookie_value})

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

    user = models.User.objects.last()
    assert user.utm == ed_utm_cookie_value


@pytest.mark.django_db
def test_login_response_with_sso_display_logged_in_cookie(
    client, verified_user
):
    response = client.post(
        reverse('account_login'),
        {'login': verified_user.email, 'password': 'password'}
    )

    assert response.cookies['sso_display_logged_in'].value == 'true'


@pytest.mark.django_db
def test_logout_response_with_sso_display_logged_in_cookie(
    authed_client
):
    response = authed_client.post(reverse('account_logout'))

    assert response.cookies['sso_display_logged_in'].value == 'false'


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_login_response_with_sso_display_logged_in_cookie(
    mocked_notification_client, client, email_confirmation
):

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

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )
    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)

    assert response.cookies['sso_display_logged_in'].value == 'true'


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_confirm_email_login_response_with_sso_handles_next(
    mocked_notification_client, client, email_confirmation
):
    querystring = '?next=http%3A//buyer.trade.great%3A8001/company-profile'
    client.post(
        reverse('account_signup') + querystring,
        data={
            'email': 'jim@example.com',
            'email2': 'jim@example.com',
            'terms_agreed': True,
            'password1': '*' * 10,
            'password2': '*' * 10,
        }
    )

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='jim@example.com',
        personalisation={'confirmation_link': mock.ANY},
        template_id=EMAIL_CONFIRMATION_TEMPLATE_ID
    )
    url = call[1]['personalisation']['confirmation_link']
    response = client.post(url)

    assert response.status_code == 302
    assert response.get('Location') == (
       "/accounts/login/"
       "?next=http%3A%2F%2Fbuyer.trade.great%3A8001%2Fcompany-profile"
    )


def test_email_verification_sent_view_feedback_url(client, settings):
    settings.HEADER_FOOTER_URLS_CONTACT_US = 'http://test.com'
    url = reverse('account_email_verification_sent')
    response = client.get(url)

    assert 'http://test.com' in response.rendered_content


@pytest.mark.parametrize('url', [
    reverse_lazy('account_signup'),
    reverse_lazy('account_reset_password'),
    reverse_lazy(
        'account_reset_password_from_key',
        kwargs={'uidb36': '123', 'key': 'foo'}
    )
], ids=(
        'signup',
        'reset password',
        'reset password from key'
)
                         )
def test_disabled_registration_views(url, client, settings):
    settings.FEATURE_DISABLE_REGISTRATION = True
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == 'https://sorry.great.gov.uk/'


@pytest.mark.django_db
def test_disabled_registration_change_password_view(authed_client, settings):
    settings.FEATURE_DISABLE_REGISTRATION = True
    response = authed_client.get(reverse('account_change_password'))
    assert response.status_code == 302
    assert response.url == 'https://sorry.great.gov.uk/'
