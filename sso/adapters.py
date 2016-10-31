from urllib.parse import urlparse

from allauth.account.adapter import DefaultAccountAdapter
import tldextract

from django.conf import settings
from django.http import QueryDict


def validate_next(next_param):
    extracted_domain = tldextract.extract(next_param)
    domain = '.'.join([extracted_domain.domain, extracted_domain.suffix])
    return (domain in settings.ALLOWED_REDIRECT_DOMAINS) or (
        extracted_domain.suffix in settings.ALLOWED_REDIRECT_DOMAINS)


class AccountAdapter(DefaultAccountAdapter):

    @staticmethod
    def get_redirect_value(request):
        if 'HTTP_REFERER' in request.META:
            referrer = request.META['HTTP_REFERER']
            parsed = urlparse(referrer)
            querydict = QueryDict(parsed.query)
            return querydict.get(settings.REDIRECT_FIELD_NAME)

    def get_email_confirmation_url(self, request, emailconfirmation):
        ret = super().get_email_confirmation_url(
            request, emailconfirmation
        )
        redirect_value = self.get_redirect_value(request)
        if redirect_value and validate_next(redirect_value):
            return '{0}?{1}={2}'.format(
                ret, settings.REDIRECT_FIELD_NAME, redirect_value
            )
        return ret
