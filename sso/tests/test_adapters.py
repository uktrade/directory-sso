from unittest.mock import patch, Mock

from sso.adapters import is_valid_redirect, AccountAdapter


def test_next_validation_returns_true_if_in_allowed_domains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.com', 'ilovecats.com']
    valid = is_valid_redirect('http://iloveexporting.com/love/')
    assert valid is True


def test_next_validation_returns_true_if_in_allowed_suffixes(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['gov.uk', 'com']
    valid = is_valid_redirect('http://www.gov.uk')
    assert valid is True
    valid = is_valid_redirect('http://exporting.com')
    assert valid is True

    # Should work with a mix of domains and suffixes
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.com', 'iloveexporting.gov.uk', 'gov.uk']
    valid = is_valid_redirect('http://iloveexporting.com/')
    assert valid is True
    valid = is_valid_redirect('http://iloveexporting.gov.uk/')
    assert valid is True
    valid = is_valid_redirect('http://exportingisgreat.gov.uk')
    assert valid is True


def test_next_validation_returns_false_if_not_in_allowed_domains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.com', 'ilovecats.com']
    valid = is_valid_redirect('http://ihateexporting.com/hate/')
    assert valid is False


def test_next_validation_returns_false_if_not_in_allowed_suffixes(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['gov.uk']
    valid = is_valid_redirect('http://iloveexporting.net')
    assert valid is False

    # Should work with a mix of domains and suffixes
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.com', 'iloveexporting.gov.uk', 'gov.uk']
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
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.co.uk', 'iloveexporting.gov.uk']
    valid = is_valid_redirect('http://www.iloveexporting.co.uk/love')
    assert valid is True

    valid = is_valid_redirect('http://love.iloveexporting.gov.uk')
    assert valid is True


def test_next_validation_copes_when_no_protocol_given(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.co.uk', 'iloveexporting.gov.uk']
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


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_default_url_if_no_next_param(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/exporting')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url'


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_default_url_if_next_param_invalid(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/export?next=http://hateexporting.com')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url'


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_modified_url_if_next_param_valid(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/export?next=http://iloveexporting.com')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == (
        'default_url?next=%2Faccounts%2Flogin%2F%3F'
        'next%3Dhttp%253A%252F%252Filoveexporting.com'
    )


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'send_mail', Mock())
@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_modified_url_if_next_param_internal(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = []
    adapter = AccountAdapter()
    request = rf.get('/export?next=/exportingismytruelove/')

    url = adapter.get_email_confirmation_url(request, None)

    assert url == (
        'default_url?next=%2Faccounts%2Flogin%2F%3F'
        'next%3D%252Fexportingismytruelove%252F'
    )
