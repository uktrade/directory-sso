from django.conf import settings


def feature_flags(request):
    return {
        'features': {
            'FEATURE_NEW_SHARED_HEADER_ENABLED': (
                settings.FEATURE_NEW_SHARED_HEADER_ENABLED
            )
        }
    }
