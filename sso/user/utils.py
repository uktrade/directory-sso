import urllib.parse

from allauth.account.utils import get_request_param
import tldextract

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.http import urlencode


ClientClass = import_string(settings.DIRECTORY_API_EXTERNAL_CLIENT_CLASS)
api_client = ClientClass(
    base_url=settings.DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET,
)


def get_url_with_redirect(url, redirect_url):
    """Adds redirect param to url"""
    if redirect_url:
        url = url + '?' + urlencode(
            {settings.REDIRECT_FIELD_NAME: redirect_url}
        )

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
        extracted_domain.suffix in settings.ALLOWED_REDIRECT_DOMAINS)


def get_redirect_url(request, redirect_field_name):
    redirect_url = settings.DEFAULT_REDIRECT_URL
    redirect_param_value = get_request_param(request, redirect_field_name)
    if redirect_param_value:
        if is_valid_redirect(urllib.parse.unquote(redirect_param_value)):
            redirect_url = redirect_param_value
    return redirect_url
