from unittest.mock import Mock, call, patch

import pytest
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import get_adapter
from django.contrib.auth import get_user_model
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from sso.adapters import AccountAdapter, SocialAccountAdapter, is_valid_redirect
from sso.tests.test_utils import not_raises
from sso.user.tests.factories import UserFactory


def test_next_validation_returns_true_if_in_allowed_domains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com', 'ilovecats.com']
    valid = is_valid_redirect('http://iloveexporting.com/love/')
    assert valid is True


def test_next_validation_returns_true_if_in_allowed_suffixes(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['gov.uk', 'com']
    valid = is_valid_redirect('http://www.gov.uk')
    assert valid is True
    valid = is_valid_redirect('http://exporting.com')
    assert valid is True

    # Should work with a mix of domains and suffixes
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com', 'iloveexporting.gov.uk', 'gov.uk']
    valid = is_valid_redirect('http://iloveexporting.com/')
    assert valid is True
    valid = is_valid_redirect('http://iloveexporting.gov.uk/')
    assert valid is True
    valid = is_valid_redirect('http://exportingisgreat.gov.uk')
    assert valid is True


def test_next_validation_returns_false_if_not_in_allowed_domains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com', 'ilovecats.com']
    valid = is_valid_redirect('http://ihateexporting.com/hate/')
    assert valid is False


def test_next_validation_returns_false_if_not_in_allowed_suffixes(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['gov.uk']
    valid = is_valid_redirect('http://iloveexporting.net')
    assert valid is False

    # Should work with a mix of domains and suffixes
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com', 'iloveexporting.gov.uk', 'gov.uk']
    valid = is_valid_redirect('http://iloveexporting.net')
    assert valid is False


def test_next_validation_copes_with_subdomains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    valid = is_valid_redirect('http://www.iloveexporting.com')
    assert valid is True
    valid = is_valid_redirect('http://love.iloveexporting.com/love/')
    assert valid is True

    settings.ALLOWED_REDIRECT_DOMAINS = ['gov.uk']
    valid = is_valid_redirect('http://www.iloveexporting.gov.uk')
    assert valid is True
    valid = is_valid_redirect('http://love.iloveexporting.gov.uk/love/')
    assert valid is True


def test_next_validation_copes_with_long_suffixes(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.co.uk', 'iloveexporting.gov.uk']
    valid = is_valid_redirect('http://www.iloveexporting.co.uk/love')
    assert valid is True

    valid = is_valid_redirect('http://love.iloveexporting.gov.uk')
    assert valid is True


def test_next_validation_copes_when_no_protocol_given(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.co.uk', 'iloveexporting.gov.uk']
    valid = is_valid_redirect('iloveexporting.co.uk/love')
    assert valid is True

    valid = is_valid_redirect('www.iloveexporting.gov.uk')
    assert valid is True


def test_next_validation_doesnt_accept_urls_starting_with_slash(settings):
    # This tests for the bug found in penetration testing (ED-661)
    # which was allowing redirects to unauthorized domains if
    # the next param started with //
    valid = is_valid_redirect('//google.com')
    assert valid is False


@patch('allauth.account.adapter.DefaultAccountAdapter.send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_default_url_if_no_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/exporting')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url'


@patch('allauth.account.adapter.DefaultAccountAdapter.send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_default_url_if_next_param_invalid(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/export?next=http://hateexporting.com')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url'


@patch('allauth.account.adapter.DefaultAccountAdapter.send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_modified_url_if_next_param_valid(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/export?next=http://iloveexporting.com')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url?next=%2Faccounts%2Flogin%2F%3Fnext%3Dhttp%253A%252F%252Filoveexporting.com'


@patch('allauth.account.adapter.DefaultAccountAdapter.send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_modified_url_if_next_param_internal(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = []
    adapter = AccountAdapter()
    request = rf.get('/export?next=/exportingismytruelove/')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url?next=%2Faccounts%2Flogin%2F%3Fnext%3D%252Fexportingismytruelove%252F'


@pytest.mark.django_db
@patch('sso.adapters.NotificationsAPIClient')
@patch('allauth.socialaccount.adapter.DefaultSocialAccountAdapter.save_user')
def test_social_adapter_creates_profile(mock_save_user, mocked_notifications, settings):
    user = UserFactory(email='foo@example.com')
    mock_save_user.return_value = user

    adapter = SocialAccountAdapter()
    adapter.save_user()

    assert user.user_profile.first_name == user.first_name
    assert user.user_profile.last_name == user.last_name

    stub = mocked_notifications().send_email_notification
    assert stub.call_count == 1
    assert stub.call_args == call(email_address='foo@example.com', template_id=settings.GOV_NOTIFY_WELCOME_TEMPLATE_ID)


class FakeSocialLogin:
    def __init__(self, email):
        self.email = email

    @property
    def user(self):
        return get_user_model()(email=self.email)

    @property
    def is_existing(self):
        return False


class FakeSocialLoginIsExisting(FakeSocialLogin):
    @property
    def is_existing(self):
        return True


@pytest.mark.django_db
@patch('allauth.account.models.EmailAddress.objects')
def test_social_adapter_pre_social_login_handles_email_dupes(mock_email, rf):
    user = UserFactory(email='foo@example.com')
    adapter = get_adapter()
    mock_email.get.return_value = user.email

    request = rf.get('/signup')
    middleware = SessionMiddleware()
    middleware.process_request(request)

    middleware = MessageMiddleware()
    middleware.process_request(request)
    request.session.save()

    with pytest.raises(ImmediateHttpResponse):
        adapter.pre_social_login(request, FakeSocialLogin('foo@example.com'))


@pytest.mark.django_db
def test_social_adapter_pre_social_login_handles_non_existing_email(rf):
    UserFactory(email='foo@example.com')
    adapter = get_adapter()

    request = rf.get('/signup')
    middleware = SessionMiddleware()
    middleware.process_request(request)

    middleware = MessageMiddleware()
    middleware.process_request(request)
    request.session.save()

    with not_raises(ImmediateHttpResponse):
        adapter.pre_social_login(request, FakeSocialLogin('foo1@example.com'))


@pytest.mark.django_db
def test_social_adapter_pre_social_login_handles_for_existing_email(rf):
    UserFactory(email='foo@example.com')
    adapter = get_adapter()

    request = rf.get('/signup')
    middleware = SessionMiddleware()
    middleware.process_request(request)

    middleware = MessageMiddleware()
    middleware.process_request(request)
    request.session.save()

    fake_social = FakeSocialLoginIsExisting('foo1@example.com')

    with not_raises(ImmediateHttpResponse):
        adapter.pre_social_login(request, fake_social)
