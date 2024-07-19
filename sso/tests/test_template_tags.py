from unittest.mock import MagicMock, Mock

from sso import constants
from sso.templatetags.canonical_url_tags import get_canonical_url
from sso.templatetags.sso_email import header_image
from sso.templatetags.sso_validation import is_valid_redirect_domain


def test_header_image_returns_constant_image():
    assert header_image() == constants.EMAIL_HEADER_IMAGE


def test_is_valid_returns_true_when_domain_valid(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com']

    is_valid = is_valid_redirect_domain('http://example.com')

    assert is_valid is True


def test_is_valid_returns_false_when_domain_invalid(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['ilovecats.com']

    is_valid = is_valid_redirect_domain('http://example.com')

    assert is_valid is False


def test_is_valid_returns_true_when_domain_internal(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com']

    is_valid = is_valid_redirect_domain('/next/')

    assert is_valid is True


def test_is_valid_returns_false_when_no_domain_supplied(settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com']

    is_valid = is_valid_redirect_domain('')
    assert is_valid is False

    is_valid = is_valid_redirect_domain(None)
    assert is_valid is False


def test_get_canonical_url_with_www(rf):
    request = Mock()
    request.scheme = 'https'
    request.path = '/sso/accounts/login/password_reset'
    request.get_host = MagicMock(return_value='www.great.com')

    context_data = {'request': request}
    canonical_url = get_canonical_url(context_data)
    assert canonical_url == 'https://www.great.com/sso/accounts/login/password_reset'


def test_get_canonical_url_without_www(rf):
    request = Mock()
    request.scheme = 'https'
    request.path = '/sso/accounts/login/password_reset'
    request.get_host = MagicMock(return_value='great.com')

    context_data = {'request': request}
    canonical_url = get_canonical_url(context_data)
    assert canonical_url == 'https://www.great.com/sso/accounts/login/password_reset'


def test_get_canonical_url_without_request():
    context_data = {}
    canonical_url = get_canonical_url(context_data)
    assert canonical_url == ''
