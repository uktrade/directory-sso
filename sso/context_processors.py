from django.conf import settings


def analytics(request):
    return {
        'analytics': {
            'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
        }
    }
