import urllib.parse

from django.conf import settings
from django.core.urlresolvers import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_request_param
from notifications_python_client import NotificationsAPIClient

from sso.user.utils import get_url_with_redirect, is_valid_redirect

EMAIL_CONFIRMATION_TEMPLATE_ID = '0c76b730-ac37-4b08-a8ba-7b34e4492853'
PASSWORD_RESET_TEMPLATE_ID = '9ef82687-4bc0-4278-b15c-a49bc9325b28',

EMAIL_TEMPLATES = {
    'account/email/email_confirmation_signup': EMAIL_CONFIRMATION_TEMPLATE_ID,
    'account/email/email_confirmation': EMAIL_CONFIRMATION_TEMPLATE_ID,

    'account/email/password_reset_key': PASSWORD_RESET_TEMPLATE_ID
}


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Constructs the email confirmation (activation) url.
        """
        redirect_url = settings.DEFAULT_REDIRECT_URL

        redirect_param_value = get_request_param(
            request, settings.REDIRECT_FIELD_NAME
        )
        if redirect_param_value:
            redirect_url = redirect_param_value

        email_confirmation_url = super().get_email_confirmation_url(
            request, emailconfirmation
        )

        if redirect_url:
            if is_valid_redirect(urllib.parse.unquote(redirect_url)):
                # This is to handle the case when user registered on one device
                # (e.g. desktop) and clicked 'confirm email' on another (e.g.
                # mobile) - if user is automatically logged in on confirm
                # (which will happen when clicking confirm on same machine)
                # login view will redirect to 'next', if not (when switching
                # browsers), user will have to log in and then will be
                # redirected
                login_url_with_next = get_url_with_redirect(
                    url=reverse('account_login'),
                    redirect_url=redirect_url
                )
                email_confirmation_url = get_url_with_redirect(
                    url=email_confirmation_url,
                    redirect_url=login_url_with_next
                )
        return email_confirmation_url

    def validate_unique_email(self, email):
        # Although email has to be unique, as it is user login, do not validate
        # it, so that e-mail enumeration is not possible - security requirement
        return email

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        user = super().save_user(
            request, user, form, commit=False
        )

        user.utm = request.COOKIES.get('ed_utm', {})

        if commit:
            user.save()

        return user

    @staticmethod
    def build_password_reset_url(context):
        """Add next param if valid redirect."""
        reset_url = context['password_reset_url']
        next_url = context['request'].POST.get('next', '')
        if next_url and is_valid_redirect(next_url):
            reset_url += '?next={next_url}'.format(next_url=next_url)
        return reset_url

    def send_mail(self, template_prefix, email, context):
        notifications_client = NotificationsAPIClient(
            settings.GOV_NOTIFY_API_KEY
        )
        template_id = EMAIL_TEMPLATES[template_prefix]

        #  build personalisation dict from context
        if template_id == PASSWORD_RESET_TEMPLATE_ID:
            personalisation = {
                'password_reset': self.build_password_reset_url(context)
            }
        else:
            personalisation = {
                'confirmation_link': context['activate_url']
            }

        notifications_client.send_email_notification(
            email_address=email,
            template_id=template_id,
            personalisation=personalisation,
        )
