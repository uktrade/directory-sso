from functools import partial

from django.conf import settings
from django.urls import reverse

from directory_constants import urls

from sso.user.utils import get_redirect_url, get_url_with_redirect, get_intent

redirect_field_name = settings.REDIRECT_FIELD_NAME


def redirect_next_processor(request):
    redirect_url = get_redirect_url(
        request=request,
        redirect_field_name=redirect_field_name
    )
    intent = get_intent(request)

    add_next = partial(get_url_with_redirect, redirect_url=redirect_url, intent=intent)
    return {
        'redirect_field_name': redirect_field_name,
        'redirect_field_value': redirect_url or None,
        'sso_logout_url': add_next(reverse('account_logout')),
        'sso_login_url': add_next(reverse('account_login')),
        'sso_reset_password_url': add_next(reverse('account_reset_password')),
        'sso_register_url': add_next(urls.domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/'),
        'sso_is_logged_in': bool(request.user and request.user.is_authenticated),
        'sso_profile_url': settings.SSO_PROFILE_URL,
    }
