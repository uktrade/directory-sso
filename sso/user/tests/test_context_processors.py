from unittest.mock import Mock

import pytest

from sso.user import context_processors


@pytest.fixture
def request_with_next_user_authenticated(rf):
    request = rf.get('/', {'next': 'http://www.example.com'})
    request.user = Mock(is_authenticated=Mock(return_value=True))
    return request


@pytest.fixture
def request_without_next_user_authenticated(rf):
    request = rf.get('/')
    request.user = Mock(is_authenticated=Mock(return_value=True))
    return request


@pytest.fixture
def request_with_next_no_user(rf):
    request = rf.get('/', {'next': 'http://www.example.com'})
    request.user = None
    return request


@pytest.fixture
def request_without_next_no_user(rf):
    request = rf.get('/')
    request.user = None
    return request


def test_redirect_next_processor_installed(settings):
    context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
    expected = 'sso.user.context_processors.redirect_next_processor'

    assert expected in context_processors


def test_redirect_next_processor_appends_next_param_user_authenticated(
    request_with_next_user_authenticated
):
    context = context_processors.redirect_next_processor(
        request_with_next_user_authenticated
    )

    assert context['redirect_field_name'] == 'next'
    assert context['redirect_field_value'] == 'http://www.example.com'
    assert context['sso_logout_url'] == (
        '/accounts/logout/?next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_login_url'] == (
        '/accounts/login/?next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_reset_password_url'] == (
        '/accounts/password/reset/?next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_register_url'] == (
        'http://profile.trade.great:8006/profile/enrol/?'
        'next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_is_logged_in'] is True


def test_redirect_next_processor_handles_no_next_param_user_authenticated(
    request_without_next_user_authenticated, settings
):
    context = context_processors.redirect_next_processor(
        request_without_next_user_authenticated
    )

    assert context['redirect_field_name'] == 'next'
    assert context['redirect_field_value'] == settings.DEFAULT_REDIRECT_URL
    assert context['sso_logout_url'] == (
        '/accounts/logout/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_login_url'] == (
        '/accounts/login/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_reset_password_url'] == (
        '/accounts/password/reset/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_register_url'] == (
        'http://profile.trade.great:8006/profile/enrol/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_is_logged_in'] is True


def test_redirect_next_processor_appends_next_param_no_user(
    request_with_next_no_user
):
    context = context_processors.redirect_next_processor(
        request_with_next_no_user
    )

    assert context['redirect_field_name'] == 'next'
    assert context['redirect_field_value'] == 'http://www.example.com'
    assert context['sso_logout_url'] == (
        '/accounts/logout/?next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_login_url'] == (
        '/accounts/login/?next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_reset_password_url'] == (
        '/accounts/password/reset/?next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_register_url'] == (
        'http://profile.trade.great:8006/profile/enrol/?'
        'next=http%3A%2F%2Fwww.example.com'
    )
    assert context['sso_is_logged_in'] is False


def test_redirect_next_processor_handles_no_next_param_no_user(
    request_without_next_no_user, settings
):
    context = context_processors.redirect_next_processor(
        request_without_next_no_user
    )

    assert context['redirect_field_name'] == 'next'
    assert context['redirect_field_value'] == settings.DEFAULT_REDIRECT_URL
    assert context['sso_logout_url'] == (
        '/accounts/logout/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_login_url'] == (
        '/accounts/login/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_reset_password_url'] == (
        '/accounts/password/reset/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_register_url'] == (
        'http://profile.trade.great:8006/profile/enrol/?'
        'next=http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2F'
    )
    assert context['sso_is_logged_in'] is False
