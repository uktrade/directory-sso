from unittest.mock import Mock

import pytest

from django.template.loader import render_to_string


@pytest.fixture
def authenticated_request(rf):
    request = rf.get('/')
    request.user = Mock(is_authenticated=lambda: True)
    return request


def test_password_reset_email(rf):
    context = {
        'password_reset_url': 'http://reset.com',
        'request': rf.get('/'),
    }
    html = render_to_string(
        'account/email/password_reset_key_message.html',
        context
    )
    assert 'http://reset.com' in html
    assert 'Reset password' in html


def test_password_reset_email_txt(rf):
    context = {
        'password_reset_url': 'http://reset.com',
        'request': rf.get('/'),
    }
    txt = render_to_string(
        'account/email/password_reset_key_message.txt',
        context
    )
    assert 'http://reset.com' in txt
    assert '?next=' not in txt


def test_confirmation_email():
    context = {
        'activate_url': 'http://confirm.com'
    }
    html = render_to_string(
        'account/email/email_confirmation_message.html', context
    )
    assert 'http://confirm.com' in html
    assert 'Verify your email address' in html


def test_google_tag_manager():
    expected_head = render_to_string('google_tag_manager_head.html')
    expected_body = render_to_string('google_tag_manager_body.html')

    html = render_to_string('base.html')

    assert expected_head in html
    assert expected_body in html
    # sanity check
    assert 'www.googletagmanager.com' in expected_head
    assert 'www.googletagmanager.com' in expected_body


def test_logged_in_header():
    context = {'sso_is_logged_in': True}
    html = render_to_string('base.html', context)

    assert '>Sign out<' in html


def test_logged_out_hedaer():
    context = {'sso_is_logged_in': False}
    html = render_to_string('base.html', context)

    assert '>Sign in<' in html


def test_utm_cookie_domain():
    context = {
        'analytics': {
            'UTM_COOKIE_DOMAIN': '.thing.com',
        }
    }
    html = render_to_string('base.html', context)

    assert '<meta id="utmCookieDomain" value=".thing.com" />' in html


def test_new_header_footer_enabled():
    context = {
        'features': {
            'FEATURE_NEW_SHARED_HEADER_ENABLED': True,
        }
    }
    html = render_to_string('base.html', context)

    assert render_to_string('directory_header_footer/header.html') in html
    assert render_to_string('directory_header_footer/footer.html') in html


def test_new_header_footer_disabled():
    context = {
        'features': {
            'FEATURE_NEW_SHARED_HEADER_ENABLED': False,
        }
    }
    html = render_to_string('base.html', context)

    assert render_to_string('directory_header_footer/header_old.html') in html
    assert render_to_string('directory_header_footer/footer_old.html') in html
