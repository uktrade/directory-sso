from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        ret = super().get_email_confirmation_url(
            request, emailconfirmation
        )
        if 'next' in request.GET:
            return '{0}?next={1}'.format(ret, request.GET['next'])
        return ret
