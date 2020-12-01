import urllib.parse

import tldextract
from allauth.account.utils import get_request_param
from allauth.socialaccount.templatetags.socialaccount import ProviderLoginURLNode
from directory_api_client import api_client
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlencode

from sso.user.models import LessonCompleted, Service, ServicePage, UserPageView


def get_url_with_redirect(url, redirect_url):
    """Adds redirect param to url"""
    if redirect_url:
        url = url + '?' + urlencode({settings.REDIRECT_FIELD_NAME: redirect_url})

    return url


def is_valid_redirect(next_param):
    # add local domain suffix because it is non-standard
    extract_with_extra_suffix = tldextract.TLDExtract(
        extra_suffixes=["great"],
    )
    extracted_domain = extract_with_extra_suffix(next_param)
    # Allow internal redirects
    is_domain = bool(extracted_domain.domain) and bool(extracted_domain.suffix)
    # NOTE: The extra is_domain check is necessary because otherwise
    # for example ?next=//satan.com would redirect even if
    # satan.com is not an allowed redirect domain
    if next_param.startswith('/') and not is_domain:
        return True

    # Otherwise check we allow that domain/suffix
    domain = '.'.join([extracted_domain.domain, extracted_domain.suffix])
    return (domain in settings.ALLOWED_REDIRECT_DOMAINS) or (
        extracted_domain.suffix in settings.ALLOWED_REDIRECT_DOMAINS
    )


def get_redirect_url(request, redirect_field_name):
    redirect_url = settings.DEFAULT_REDIRECT_URL
    redirect_param_value = get_request_param(request, redirect_field_name)
    if redirect_param_value:
        if is_valid_redirect(urllib.parse.unquote(redirect_param_value)):
            redirect_url = redirect_param_value
    return redirect_url


def user_has_company(sso_id):
    response = api_client.supplier.retrieve_profile(sso_id)
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return bool(response.json()['company'])


def user_has_profile(user):
    try:
        user.user_profile
    except ObjectDoesNotExist:
        return False
    else:
        return True


def get_login_provider_url(request, provider_id):
    node = ProviderLoginURLNode(provider_id=f"'{provider_id}'", params={})
    return node.render({'request': request})


def get_social_account_image(account):
    if account.provider == 'linkedin_oauth2':
        for size_variant in account.extra_data.get('profilePicture', {}).get('displayImage~', {}).get('elements', {}):
            for image in size_variant['identifiers']:
                return image['identifier']
    elif account.provider == 'google':
        return account.extra_data.get('picture')


def set_page_view(user, service_name, page_name):
    service, created = Service.objects.get_or_create(name=service_name)
    service_page, created = ServicePage.objects.get_or_create(service=service, page_name=page_name)
    user_page_view, created = UserPageView.objects.get_or_create(service_page=service_page, user=user)
    return user_page_view


def get_page_view(user, service_name, page_name=None):
    try:
        service = Service.objects.get(name=service_name)
        if page_name:
            return UserPageView.objects.filter(
                user=user, service_page__service=service, service_page__page_name=page_name
            )
        return UserPageView.objects.filter(user=user, service_page__service=service)
    except ObjectDoesNotExist:
        pass


def set_lesson_completed(user, service_name, lesson_name, lesson, module):
    service, created = Service.objects.get_or_create(name=service_name)
    lesson_completed, created = LessonCompleted.objects.get_or_create(
        user=user,
        service=service,
        lesson_page=lesson_name,
        lesson=lesson,
        module=module,
    )
    return lesson_completed


def get_lesson_completed(user, service, **filter_dict):
    try:
        service = Service.objects.get(name=service)
        return LessonCompleted.objects.filter(user=user, service=service, **filter_dict)
    except ObjectDoesNotExist:
        return None
