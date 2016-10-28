from unittest.mock import patch

from ..adapters import validate_next


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
