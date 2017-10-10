from sso import context_processors


def test_analytics(rf, settings):
    settings.UTM_COOKIE_DOMAIN = '.thing.com'

    actual = context_processors.analytics(None)

    assert actual == {
        'analytics': {
            'UTM_COOKIE_DOMAIN': '.thing.com',
        }
    }


def test_analytics_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'sso.context_processors.analytics' in processors


def test_feature_returns_expected_features(settings):
    settings.FEATURE_NEW_SHARED_HEADER_ENABLED = True

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
            'FEATURE_NEW_SHARED_HEADER_ENABLED': True
        }
    }
