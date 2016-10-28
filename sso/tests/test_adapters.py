from unittest.mock import patch, Mock

import pytest
from django.core.exceptions import ValidationError

from ..adapters import validate_next, AccountAdapter


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.com', 'ilovecats.com'])
def test_next_validation_returns_true_if_in_allowed_domains():
    valid = validate_next('http://iloveexporting.com/love/')
    assert valid is True


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.com', 'ilovecats.com'])
def test_next_validation_returns_false_if_not_in_allowed_domains():
    valid = validate_next('http://ihateexporting.com/hate/')
    assert valid is False


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.com'])
def test_next_validation_copes_with_subdomains():
    valid = validate_next('http://www.iloveexporting.com')
    assert valid is True

    valid = validate_next('http://love.iloveexporting.com/love/')
    assert valid is True


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.co.uk', 'iloveexporting.gov.uk'])
def test_next_validation_copes_with_long_suffixes():
    valid = validate_next('http://www.iloveexporting.co.uk/love')
    assert valid is True

    valid = validate_next('http://love.iloveexporting.gov.uk')
    assert valid is True


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.co.uk', 'iloveexporting.gov.uk'])
def test_next_validation_copes_when_no_protocol_given():
    valid = validate_next('iloveexporting.co.uk/love')
    assert valid is True

    valid = validate_next('www.iloveexporting.gov.uk')
    assert valid is True


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.com'])
@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock())
def test_account_adapter_raises_exception_if_next_param_invalid(rf):
    adapter = AccountAdapter()
    request = rf.get('/exporting?next=http://hateexporting.com')

    with pytest.raises(ValidationError):
        adapter.get_email_confirmation_url(request, None)


@patch('django.conf.settings.ALLOWED_REDIRECT_DOMAINS',
       ['iloveexporting.com'])
@patch('allauth.account.adapter.DefaultAccountAdapter.'
       'get_email_confirmation_url', Mock())
def test_account_adapter_doesnt_raise_exception_if_next_param_valid(rf):
    adapter = AccountAdapter()
    request = rf.get('/exporting?next=http://iloveexporting.com')

    try:
        adapter.get_email_confirmation_url(request, None)
    except ValidationError:
        raise AssertionError("Account Adapter is raising exception on "
                             "valid next param")
