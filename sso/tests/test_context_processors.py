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


def test_feature_returns_expected_features(rf, settings):
    settings.FEATURE_NEW_HEADER_FOOTER_ENABLED = 1

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
            'FEATURE_NEW_HEADER_FOOTER_ENABLED': 1
        }
    }
