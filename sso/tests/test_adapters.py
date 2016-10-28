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
