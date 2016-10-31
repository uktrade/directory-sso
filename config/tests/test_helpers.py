from ..helpers import validate_domain


def test_validate_domain_returns_true_for_valid_domains():
    assert validate_domain('http://google.com') is True
    assert validate_domain('google.com') is True


def test_validate_domain_returns_true_for_valid_suffixes():
    assert validate_domain('gov.uk') is True
    assert validate_domain('.gov.uk') is True
    assert validate_domain('com') is True
    assert validate_domain('.com') is True


def test_validate_domain_returns_false_for_invalid_domains():
    assert validate_domain('http://') is False
    assert validate_domain('blabla') is False
    assert validate_domain('http://blabla') is False
    assert validate_domain('http://www.blablabla') is False


def test_validate_domain_returns_false_for_scheme_suffix_and_no_domain():
    # Because http://gov.uk as a setting just seems weird and is likely
    # a mistake. When providing suffix we expect "gov.uk" in settings
    assert validate_domain('http://gov.uk') is False
    assert validate_domain('http://.gov.uk') is False
    assert validate_domain('http://com') is False
    assert validate_domain('http://.com') is False


def test_validate_domain_returns_false_if_subdomain_included():
    assert validate_domain('http://mail.google.com') is False
    assert validate_domain('mail.google.com') is False


def test_validate_domain_returns_false_if_path_or_params_included():
    assert validate_domain('http://google.com?q=exporting') is False
    assert validate_domain('http://google.com/exporing') is False
    assert validate_domain('google.com?q=exporting') is False
    assert validate_domain('google.com/exporing') is False
