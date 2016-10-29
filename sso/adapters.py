from allauth.account.adapter import DefaultAccountAdapter
import tldextract
from django.conf import settings


def validate_next(next_param):
    extracted_domain = tldextract.extract(next_param)
    domain = '.'.join([extracted_domain.domain, extracted_domain.suffix])
    return domain in settings.ALLOWED_REDIRECT_DOMAINS


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        ret = super().get_email_confirmation_url(
            request, emailconfirmation
        )
        if 'next' in request.GET and validate_next(request.GET['next']):
            return '{0}?next={1}'.format(ret, request.GET['next'])
        return ret
