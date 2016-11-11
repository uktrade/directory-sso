from django.conf import settings
from django.utils.http import urlencode

import tldextract


def get_url_with_redirect(url, redirect_url):
    """Adds redirect param to url"""
    if redirect_url:
        url = url + '?' + urlencode(
            {settings.REDIRECT_FIELD_NAME: redirect_url}
        )

    return url


def is_valid_redirect(next_param):
    # Allow internal redirects
    if next_param.startswith('/'):
        return True

    # Otherwise check we allow that domain/suffix
    extracted_domain = tldextract.extract(next_param)
    domain = '.'.join([extracted_domain.domain, extracted_domain.suffix])
    return (domain in settings.ALLOWED_REDIRECT_DOMAINS) or (
        extracted_domain.suffix in settings.ALLOWED_REDIRECT_DOMAINS)
