from sso.templatetags.sso_validation import is_valid_redirect_domain
from sso.templatetags.sso_email import header_image
from sso import constants


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
