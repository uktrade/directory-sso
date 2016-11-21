import pytest

from sso.user import context_processors


@pytest.fixture
def request_with_next(rf):
    return rf.get('/', {'next': 'http://www.example.com'})


@pytest.fixture
def request_without_next(rf):
    return rf.get('/')


def test_redirect_next_processor_installed(settings):
    context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
    expected = 'sso.user.context_processors.redirect_next_processor'

    assert expected in context_processors


def test_redirect_next_processor_appends_next_param(request_with_next):
    context = context_processors.redirect_next_processor(request_with_next)

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
    assert context['sso_signup_url'] == (
        '/accounts/signup/?next=http%3A%2F%2Fwww.example.com'
    )


def test_redirect_next_processor_handles_no_next_param(
    request_without_next, settings
):
    context = context_processors.redirect_next_processor(request_without_next)

    assert context['redirect_field_name'] == 'next'
    assert context['redirect_field_value'] == settings.DEFAULT_REDIRECT_URL
    assert context['sso_logout_url'] == (
        '/accounts/logout/?'
        'next=https%3A%2F%2Ffind-a-buyer.export.great.gov.uk%2F'
    )
    assert context['sso_login_url'] == (
        '/accounts/login/?'
        'next=https%3A%2F%2Ffind-a-buyer.export.great.gov.uk%2F'
    )
    assert context['sso_reset_password_url'] == (
        '/accounts/password/reset/?'
        'next=https%3A%2F%2Ffind-a-buyer.export.great.gov.uk%2F'
    )
    assert context['sso_signup_url'] == (
        '/accounts/signup/?'
        'next=https%3A%2F%2Ffind-a-buyer.export.great.gov.uk%2F'
    )
