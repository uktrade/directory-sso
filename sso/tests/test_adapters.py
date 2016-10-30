from unittest.mock import patch, Mock

from ..adapters import validate_next, AccountAdapter


def test_next_validation_returns_true_if_in_allowed_domains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.com', 'ilovecats.com']
    valid = validate_next('http://iloveexporting.com/love/')
    assert valid is True


def test_next_validation_returns_false_if_not_in_allowed_domains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.com', 'ilovecats.com']
    valid = validate_next('http://ihateexporting.com/hate/')
    assert valid is False


def test_next_validation_copes_with_subdomains(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    valid = validate_next('http://www.iloveexporting.com')
    assert valid is True

    valid = validate_next('http://love.iloveexporting.com/love/')
    assert valid is True


def test_next_validation_copes_with_long_suffixes(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.co.uk', 'iloveexporting.gov.uk']
    valid = validate_next('http://www.iloveexporting.co.uk/love')
    assert valid is True

    valid = validate_next('http://love.iloveexporting.gov.uk')
    assert valid is True


def test_next_validation_copes_when_no_protocol_given(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = [
        'iloveexporting.co.uk', 'iloveexporting.gov.uk']
    valid = validate_next('iloveexporting.co.uk/love')
    assert valid is True

    valid = validate_next('www.iloveexporting.gov.uk')
    assert valid is True


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_default_url_if_no_next_param(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/exporting')
    request.META['HTTP_REFERER'] = '/exporting'

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url'


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_default_url_if_next_param_invalid(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/export?next=http://hateexporting.com')
    request.META['HTTP_REFERER'] = '/export?next=http://hateexporting.com'

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url'


@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock(return_value='default_url'))
def test_account_adapter_returns_modified_url_if_next_param_valid(
        rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['iloveexporting.com']
    adapter = AccountAdapter()
    request = rf.get('/export?next=http://iloveexporting.com')
    request.META['HTTP_REFERER'] = '/export?next=http://iloveexporting.com'

    url = adapter.get_email_confirmation_url(request, None)

    assert url == 'default_url?next=http://iloveexporting.com'
