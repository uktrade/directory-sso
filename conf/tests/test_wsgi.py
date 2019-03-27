from unittest import mock

from bs4 import BeautifulSoup
import pytest

from conf import wsgi


@pytest.mark.django_db
@pytest.mark.parametrize('script_name,prefix', (
    ('/sso', '/sso/accounts/'),
    ('', '/accounts/')
))
def test_set_script_name(rf, script_name, prefix):
    environ = rf._base_environ(
        PATH_INFO='/accounts/password/reset/',
        CONTENT_TYPE="text/html; charset=utf-8",
        REQUEST_METHOD="GET",
        HTTP_X_SCRIPT_NAME=script_name,
    )

    response = wsgi.application(environ=environ, start_response=mock.Mock)

    assert response.status_code == 200

    soup = BeautifulSoup(response.content, 'html.parser')

    element = soup.find(id='header-sign-in-link')
    assert element.attrs['href'].startswith(prefix)
