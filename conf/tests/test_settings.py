import os
from unittest import mock

from django.contrib.staticfiles.storage import staticfiles_storage
from django.test.utils import override_script_prefix


@mock.patch.dict(os.environ, {'STATIC_HOST': 'http://static.com/'})
@override_script_prefix('/sso/')
def test_script_aware_static_host_set(settings):
    settings.STATICFILES_STORAGE = (
        'django.contrib.staticfiles.storage.StaticFilesStorage'
    )

    expected = 'http://static.com/sso/static/javascripts/index.js'

    assert staticfiles_storage.url('javascripts/index.js') == expected


@override_script_prefix('/sso/')
def test_script_aware_static_host_not_set(settings):
    settings.STATICFILES_STORAGE = (
        'django.contrib.staticfiles.storage.StaticFilesStorage'
    )

    actual = staticfiles_storage.url('javascripts/index.js')
    expected = '/sso/static/javascripts/index.js'

    assert actual == expected


@override_script_prefix('/')
@mock.patch.dict(os.environ, {'STATIC_HOST': 'http://static.com/'})
def test_script_aware_static_host_set_no_script(settings):
    settings.STATICFILES_STORAGE = (
        'django.contrib.staticfiles.storage.StaticFilesStorage'
    )
    expected = 'http://static.com/static/javascripts/index.js'

    assert staticfiles_storage.url('javascripts/index.js') == expected


@override_script_prefix('/')
def test_script_aware_static_host_not_set_no_script(settings):
    settings.STATICFILES_STORAGE = (
        'django.contrib.staticfiles.storage.StaticFilesStorage'
    )

    actual = staticfiles_storage.url('javascripts/index.js')
    expected = '/static/javascripts/index.js'

    assert actual == expected
