import sys
from importlib import import_module, reload

from django.conf import settings
from django.urls import clear_url_caches

from core.helpers import is_valid_domain


def reload_urlconf():
    clear_url_caches()
    reload_module(settings.ROOT_URLCONF)


def reload_module(module):
    if module in sys.modules:
        reload(sys.modules[module])
    else:
        import_module(module)


def test_is_valid_domain_returns_true_for_valid_domains():
    assert is_valid_domain('http://google.com') is True
    assert is_valid_domain('google.com') is True


def test_is_valid_domain_returns_true_for_valid_suffixes():
    assert is_valid_domain('gov.uk') is True
    assert is_valid_domain('.gov.uk') is True
    assert is_valid_domain('com') is True
    assert is_valid_domain('.com') is True


def test_is_valid_domain_returns_false_for_invalid_domains():
    assert is_valid_domain('http://') is False
    assert is_valid_domain('blabla') is False
    assert is_valid_domain('http://blabla') is False
    assert is_valid_domain('http://www.blablabla') is False


def test_is_valid_domain_returns_false_for_scheme_suffix_and_no_domain():
    # Because http://gov.uk as a setting just seems weird and is likely
    # a mistake. When providing suffix we expect "gov.uk" in settings
    assert is_valid_domain('http://gov.uk') is False
    assert is_valid_domain('http://.gov.uk') is False
    assert is_valid_domain('http://com') is False
    assert is_valid_domain('http://.com') is False


def test_is_valid_domain_returns_false_if_subdomain_included():
    assert is_valid_domain('http://mail.google.com') is False
    assert is_valid_domain('mail.google.com') is False


def test_is_valid_domain_returns_false_if_path_or_params_included():
    assert is_valid_domain('http://google.com?q=exporting') is False
    assert is_valid_domain('http://google.com/exporing') is False
    assert is_valid_domain('google.com?q=exporting') is False
    assert is_valid_domain('google.com/exporing') is False
