from urllib.parse import urlparse

from allauth.account.adapter import DefaultAccountAdapter

from django.conf import settings
from django.http import QueryDict


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
        if redirect_value:
            return '{0}?{1}={2}'.format(
                ret, settings.REDIRECT_FIELD_NAME, redirect_value
            )
        return ret
