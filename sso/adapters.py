from allauth.account.adapter import DefaultAccountAdapter
from urllib.parse import urlparse
from django.conf import settings


def validate_next(next_param):
    domain = urlparse(next_param).netloc
    return domain in settings.ALLOWED_REDIRECT_DOMAINS


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        ret = super().get_email_confirmation_url(
            request, emailconfirmation
        )
        if 'next' in request.GET:
            return '{0}?next={1}'.format(ret, request.GET['next'])
        return ret
