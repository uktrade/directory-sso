from unittest.mock import Mock

import pytest

from django.template.loader import render_to_string


@pytest.fixture
def authenticated_request(rf):
    request = rf.get('/')
    request.user = Mock(is_authenticated=lambda: True)
    return request


def test_logged_in_header():
    context = {'sso_is_logged_in': True}
    html = render_to_string('base.html', context)

    assert '>Sign out<' in html


def test_logged_out_hedaer():
    context = {'sso_is_logged_in': False}
    html = render_to_string('base.html', context)

    assert '>Sign in<' in html
