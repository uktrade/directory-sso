from unittest import mock
from unittest.mock import patch

import pytest
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.socialaccount.models import SocialAccount
from directory_api_client import api_client
from directory_constants import urls
from django.conf import settings
from django.contrib.sessions.models import Session
from django.urls import reverse

from core.tests.helpers import create_response
from sso.user import models
from sso.user.tests import factories
from sso.verification.models import VerificationCode


@pytest.fixture(autouse=True)
def mock_retrieve_company():
    data = {
        'name': 'Cool Company',
        'is_publishable': True,
        'expertise_products_services': {},
        'is_identity_check_message_sent': False,
    }
    response = create_response(data)
    patch = mock.patch.object(api_client.company, 'profile_retrieve', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_retrieve_supplier():
    data = {'company': None}
    response = create_response(data)
    patch = mock.patch.object(api_client.supplier, 'retrieve_profile', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture
def user():
    profile = factories.UserProfileFactory.create(user__email='test@example.com')
    user = profile.user
    user.set_password('password')
    user.save()
    return profile.user


@pytest.fixture(autouse=False)
def social_user():

    profile = factories.UserProfileFactory.create(user__email='test@example.com')
    user = profile.user
    user.set_password('password')
    account = SocialAccount(
        user_id=user.id,
        extra_data={
            'id': user.id,
            'email': user.email,
            'verified_email': True,
            'name': 'Jim Example',
            'given_name': 'Jim',
            'family_name': 'Example',
            'locale': 'en',
        },
        provider='google',
    )
    account.save()
    user.socialaccount = account
    user.save()
    return profile.user


@pytest.fixture
def verified_user():
    profile = factories.UserProfileFactory.create(user__email='verified@example.com')
    user = profile.user
    user.set_password('password')
    user.save()
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user


@pytest.fixture
def authed_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def email(user):
    return EmailAddress.objects.create(user=user, email='a@b.com', verified=False, primary=True)


@pytest.fixture
def email_confirmation(email):
    return EmailConfirmationHMAC(email)


@pytest.mark.django_db
def test_account_login_views(client):
    response = client.get(reverse('account_login'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_signup_views(client):
    response = client.get(reverse('account_signup'))
    assert response.status_code == 302
    assert response.url == urls.domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/'


@pytest.mark.django_db
def test_login_redirect_next_param_oauth2(client, settings, verified_user, mock_retrieve_supplier):
    mock_retrieve_supplier.return_value = create_response({'company': 12})

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
        {'login': verified_user.email, 'password': 'password'},
    )

    assert response.status_code == 302
    assert response.url == (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as'
        '&redirect_uri=https%3A%2F%2Fuktieig-secondary.staging.'
        'dxw.net%2Fusers%2Fauth%2Fexporting_is_great%2Fcallback&'
        'response_type=code&scope=profile&state=23947asdoih4380'
    )


@pytest.mark.django_db
def test_login_redirect_no_profile(client, verified_user, settings):
    verified_user.user_profile.delete()
    response = client.post(reverse('account_login'), {'login': verified_user.email, 'password': 'password'})

    assert response.status_code == 302
    assert response.url == 'http://profile.trade.great:8006/profile/enrol/?backfill-details-intent=true'


@pytest.mark.django_db
@patch('sso.adapters.NotificationsAPIClient')
def test_login_redirect_no_profile_unverified(mock_notification, client, user, settings):

    user.user_profile.delete()
    response = client.post(reverse('account_login'), {'login': user.email, 'password': 'password'})

    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    assert mock_notification().send_email_notification.call_count == 1


@pytest.mark.django_db
@patch('sso.adapters.NotificationsAPIClient')
def test_login_redirect_new_flow_unverified(mock_notification, client, user, settings):
    VerificationCode.objects.create(user=user)
    response = client.post(reverse('account_login'), {'login': user.email, 'password': 'password'})

    assert response.status_code == 302
    assert response.url == 'http://profile.trade.great:8006/profile/enrol/resend-verification/resend/'
    assert mock_notification().send_email_notification.call_count == 0


@pytest.mark.django_db
@patch('sso.adapters.NotificationsAPIClient')
def test_login_redirect_no_business_unverified(mock_notification, client, user, settings, mock_retrieve_supplier):
    mock_retrieve_supplier.return_value = create_response({'company': None})
    response = client.post(reverse('account_login'), {'login': user.email, 'password': 'password'})

    assert response.status_code == 302
    assert response.url == reverse("account_email_verification_sent")
    assert mock_notification().send_email_notification.call_count == 1


@pytest.mark.django_db
def test_login_redirect_default_param_if_no_next_param(client, verified_user, settings, mock_retrieve_supplier):
    mock_retrieve_supplier.return_value = create_response({'company': 12})

    settings.DEFAULT_REDIRECT_URL = 'http://www.example.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    response = client.post(reverse('account_login'), {'login': verified_user.email, 'password': 'password'})

    assert response.status_code == 302
    assert response.url == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_internal(client, settings, verified_user, mock_retrieve_supplier):
    mock_retrieve_supplier.return_value = create_response({'company': 12})

    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = '/i-love-cats/'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected), {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_valid(client, settings, verified_user, mock_retrieve_supplier):
    mock_retrieve_supplier.return_value = create_response({'company': 12})

    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    expected = 'http://example.com/?param=test'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=expected), {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.django_db
def test_login_redirect_next_param_if_next_param_invalid(client, settings, verified_user, mock_retrieve_supplier):
    mock_retrieve_supplier.return_value = create_response({'company': 12})

    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    url = reverse('account_login')
    next_param = 'http://example.com'

    response = client.post(
        '{url}?next={next}'.format(url=url, next=next_param), {'login': verified_user.email, 'password': 'password'}
    )

    assert response.status_code == 302
    assert response.url == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_oath2(authed_client, settings):
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

    response = authed_client.post('{url}?next={next}'.format(url=url, next=redirect_field_value))

    assert response.status_code == 302
    assert response.url == (
        '/oauth2/authorize/?client_id=aisudhgfg943287895as'
        '&redirect_uri=https%3A%2F%2Fuktieig-secondary.staging.'
        'dxw.net%2Fusers%2Fauth%2Fexporting_is_great%2Fcallback&'
        'response_type=code&scope=profile&state=23947asdoih4380'
    )


@pytest.mark.django_db
def test_logout_redirect_default_param_if_no_next_param(authed_client, settings):
    settings.DEFAULT_REDIRECT_URL = 'http://www.example.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['http://www.example.com', 'http://www.other.com']
    response = authed_client.post(reverse('account_logout'))

    assert response.status_code == 302
    assert response.url == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_valid(authed_client, settings):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_logout')
    expected = 'http://example.com/?param=test'

    response = authed_client.post('{url}?next={next}'.format(url=url, next=expected))

    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_invalid(authed_client, settings):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    url = reverse('account_logout')
    next_param = 'http://example.com'

    response = authed_client.post('{url}?next={next}'.format(url=url, next=next_param))

    assert response.status_code == 302
    assert response.url == settings.DEFAULT_REDIRECT_URL


@pytest.mark.django_db
def test_logout_redirect_next_param_if_next_param_internal(authed_client, settings):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['http://www.example.com', 'http://www.other.com']
    url = reverse('account_logout')
    expected = '/exporting/'

    response = authed_client.post('{url}?next={next}'.format(url=url, next=expected))

    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.django_db
def test_confirm_email_invalid_key(settings, client, email_confirmation):
    response = client.get('/accounts/confirm-email/invalid/')

    assert response.status_code == 200
    assert "confirmation link expired or is invalid" in str(response.content)


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_default_param_if_no_next_param(mocked_notification_client, settings, client, user):
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = 'ZaronZ0xos'
    # submit form and send 'password reset link' email without a 'next' param
    client.post(reverse('account_reset_password'), data={'email': user.email})
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID,
    )
    url = call[1]['personalisation']['password_reset']

    preflight_response = client.get(url)
    response = client.post(preflight_response.url, {'password1': new_password, 'password2': new_password})

    assert response.status_code == 302
    assert response.url == reverse('account_email_verification_sent')


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_social_login(mocked_notification_client, settings, client, social_user):
    client.post(reverse('account_reset_password'), data={'email': social_user.email})
    assert mocked_notification_client().send_email_notification.called is True
    assert mocked_notification_client().send_email_notification.call_args == mock.call(
        email_address=social_user.email,
        personalisation={'login_link': settings.MAGNA_URL + '/login/'},
        template_id=settings.GOV_NOTIFY_SOCIAL_PASSWORD_RESET_TEMPLATE_ID,
    )


@pytest.mark.django_db
def test_password_reset_invalid_key(client, user):
    response = client.get('/accounts/password/reset/key/gc-asdf/')

    assert "Bad Token" in str(response.content)


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_no_internal_session(mocked_notification_client, client, user):
    client.post(reverse('account_reset_password'), data={'email': user.email})
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID,
    )
    url = call[1]['personalisation']['password_reset']

    preflight_response = client.get(url)
    # going incognito
    client.session.flush()

    new_password = 'new'
    response = client.post(preflight_response.url, {'password1': new_password, 'password2': new_password})

    assert "Bad Token" in str(response.content)


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_valid(mocked_notification_client, settings, client, user):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = 'ZaronZ0xos'
    password_reset_url = reverse('account_reset_password')
    expected = reverse('account_email_verification_sent')

    # submit form and send 'password reset link' email with a 'next' param
    client.post('{url}?next={next}'.format(url=password_reset_url, next=expected), data={'email': user.email})
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID,
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    data = {'password1': new_password, 'password2': new_password, 'next': expected}
    preflight_response = client.post(url)
    response = client.post(
        preflight_response.url,
        data,
    )

    assert response.status_code == 302
    assert response.url == expected


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_invalid(mocked_notification_client, settings, client, user):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    new_password = 'ZaronZ0xos'
    password_reset_url = reverse('account_reset_password')
    next_param = 'http://www.example.com'

    # submit form and send 'password reset link' email with a 'next' param
    client.post('{url}?next={next}'.format(url=password_reset_url, next=next_param), data={'email': user.email})
    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID,
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    preflight_response = client.post(url)
    response = client.post(preflight_response.url, {'password1': new_password, 'password2': new_password})

    assert response.status_code == 302
    assert response.url == reverse('account_email_verification_sent')


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_redirect_next_param_if_next_param_internal(mocked_notification_client, settings, client, user):
    settings.DEFAULT_REDIRECT_URL = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    new_password = 'ZaronZ0xos'
    password_reset_url = reverse('account_reset_password')
    expected = reverse('account_email_verification_sent')

    # submit form and send 'password reset link' email with a 'next' param
    client.post(
        '{url}?next={next}'.format(url=password_reset_url, next=expected), data={'email': user.email, 'next': expected}
    )

    assert mocked_notification_client().send_email_notification.called is True
    call = mocked_notification_client().send_email_notification.call_args
    assert call == mock.call(
        email_address='test@example.com',
        personalisation={'password_reset': mock.ANY},
        template_id=settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID,
    )
    url = call[1]['personalisation']['password_reset']

    # Reset the password
    preflight_response = client.post(url)
    response = client.post(preflight_response.url, {'password1': new_password, 'password2': new_password})

    assert response.status_code == 302
    assert response.url == expected


@patch('sso.adapters.NotificationsAPIClient')
@pytest.mark.django_db
def test_password_reset_doesnt_allow_email_enumeration(mocked_notification_client, settings, client, user):
    redirect_to = 'http://other.com'
    settings.ALLOWED_REDIRECT_DOMAINS = ['other.com']
    account_reset_password_url = "{}?next={}".format(reverse('account_reset_password'), redirect_to)

    data = {'email': 'imaginaryemail@example.com', 'next': redirect_to}
    response = client.post(account_reset_password_url, data=data)

    # don't send an email cause no account exists
    assert mocked_notification_client().send_email_notification.called is False
    # but redirect anyway so attackers dont find out if it exists
    assert response.status_code == 302
    assert response.url == reverse('account_reset_password_done')


@pytest.mark.django_db
def test_login_page_signup_has_next(client, settings, verified_user):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    next_value = 'http://example.com/?param=test'

    response = client.get('{url}?next={next}'.format(url=url, next=next_value))

    assert response.status_code == 200

    expected_signup_url = (
        'http://profile.trade.great:8006/profile/enrol/?next=http%3A%2F%2Fexample.com%2F%3Fparam%3Dtest'
    )
    assert expected_signup_url in response.rendered_content


@pytest.mark.django_db
def test_login_page_password_reset_has_next(client, settings, verified_user):
    settings.DEFAULT_REDIRECT_URL = 'http://www.other.com/?param=test'
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com', 'other.com']
    url = reverse('account_login')
    next_value = 'http://example.com/?param=test'

    response = client.get('{url}?next={next}'.format(url=url, next=next_value))

    assert response.status_code == 200

    expected_password_reset_url = '/password/reset/?next=http%3A%2F%2Fexample.com%2F%3Fparam%3Dtest'
    assert expected_password_reset_url in response.rendered_content


@patch('sso.adapters.NotificationsAPIClient', mock.Mock())
@pytest.mark.django_db
def test_signup_saves_hashed_id(settings, client, email_confirmation):
    client.post(
        reverse('account_signup'),
        data={
            'email': 'jim@example.com',
            'email2': 'jim@example.com',
            'terms_agreed': True,
            'password1': 'ZaronZ0xos',
            'password2': 'ZaronZ0xos',
        },
    )

    user = models.User.objects.last()

    assert user.hashed_uuid != '{}'
    assert user.hashed_uuid is not None


@pytest.mark.django_db
@pytest.mark.parametrize('is_secure,expected', [(True, True), (False, '')])
def test_sso_display_logged_in_cookie_secure(authed_client, settings, is_secure, expected):
    settings.SESSION_COOKIE_SECURE = is_secure

    response = authed_client.get(reverse('account_login'))

    assert response.cookies['sso_display_logged_in']['secure'] == expected


@pytest.mark.django_db
def test_login_response_with_sso_display_logged_in_cookie(client, verified_user):
    response = client.post(reverse('account_login'), {'login': verified_user.email, 'password': 'password'})

    assert response.cookies['sso_display_logged_in'].value == 'true'


@pytest.mark.django_db
def test_logout_response_with_sso_display_logged_in_cookie(authed_client):
    response = authed_client.post(reverse('account_logout'))

    assert response.cookies['sso_display_logged_in'].value == 'false'


@pytest.mark.django_db
def test_logout_flush_session_if_cookie_with_session_key(client):
    session_key = client.session.session_key

    assert Session.objects.get(session_key=session_key)

    client.cookies['session_key'] = session_key
    client.post(reverse('account_logout'))

    with pytest.raises(Session.DoesNotExist):
        Session.objects.get(session_key=session_key)


def test_email_verification_sent_view_feedback_url(client, settings):
    url = reverse('account_email_verification_sent')
    response = client.get(url)

    assert urls.domestic.CONTACT_US in response.rendered_content


@pytest.mark.django_db
def test_disabled_registration_account_change_password_view(authed_client, settings):
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS, 'DISABLE_REGISTRATION_ON': True}
    response = authed_client.get(reverse('account_change_password'))
    assert response.status_code == 302
    assert response.url == 'https://sorry.great.gov.uk/'


def test_login_via_linkedin(client, settings):
    url = reverse('login-via-linkedin')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == '/login-providers/linkedin_oauth2/login/'


def test_login_via_google(client, settings):
    url = reverse('login-via-google')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == '/login-providers/google/login/'
