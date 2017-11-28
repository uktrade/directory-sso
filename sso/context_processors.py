from django.conf import settings
from django.urls import reverse


def analytics(request):
    return {
        'analytics': {
            'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
        }
    }


def feature_flags(request):
    return {
        'features': {
            'FEATURE_NEW_SHARED_HEADER_ENABLED': (
                settings.FEATURE_NEW_SHARED_HEADER_ENABLED
            )
        }
    }
