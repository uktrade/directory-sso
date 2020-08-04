import urllib.parse

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.utils import get_request_param
from directory_constants.urls import domestic
from notifications_python_client import NotificationsAPIClient

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect

from sso.user.utils import get_url_with_redirect, is_valid_redirect
from sso.verification.models import VerificationCode
from sso.user.models import UserProfile


EMAIL_TEMPLATES = {
    'account/email/email_confirmation_signup': settings.GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID,
    'account/email/email_confirmation': settings.GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID,
    'account/email/password_reset_key': settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID
}


class AccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Constructs the email confirmation (activation) url.
        """
        redirect_url = settings.DEFAULT_REDIRECT_URL

        redirect_param_value = get_request_param(request, settings.REDIRECT_FIELD_NAME)
        if redirect_param_value:
            redirect_url = redirect_param_value

        email_confirmation_url = super().get_email_confirmation_url(request, emailconfirmation)

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
        user = super().save_user(request, user, form, commit=False)

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
        template_id = EMAIL_TEMPLATES[template_prefix]

        #  build personalisation dict from context
        if template_id == settings.GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID:
            personalisation = {
                'password_reset': self.build_password_reset_url(context)
            }
        else:
            personalisation = {
                'confirmation_link': context['activate_url']
            }

        notifications_client = NotificationsAPIClient(
            settings.GOV_NOTIFY_API_KEY
        )
        notifications_client.send_email_notification(
            email_address=email,
            template_id=template_id,
            personalisation=personalisation,
        )

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # Send the email only if the user signed up via the "old flow". The "new flow" involved a verification code
        try:
            emailconfirmation.email_address.user.verification_code
        except VerificationCode.DoesNotExist:
            return super().send_confirmation_mail(request=request, emailconfirmation=emailconfirmation, signup=signup)
        else:
            pass

    def respond_email_verification_sent(self, request, user):
        # Checking if using "old flow" or "new flow".
        try:
            user.verification_code
        except VerificationCode.DoesNotExist:
            return super().respond_email_verification_sent(request, user)
        else:
            return redirect(domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/resend-verification/resend/')

    def is_safe_url(self, url):
        if url:
            return is_valid_redirect(urllib.parse.unquote(url))


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, *args, **kwargs):
        user = super().save_user(*args, **kwargs)
        UserProfile.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.send_welcome_email(user.email)
        return user

    @staticmethod
    def send_welcome_email(email):
        client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
        client.send_email_notification(
            email_address=email,
            template_id=settings.GOV_NOTIFY_WELCOME_TEMPLATE_ID,
        )

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).
        """

        # Ignore existing social accounts
        if sociallogin.is_existing:
            return

        # Check if given email address already exists
        try:
            social_user = sociallogin.user
            social_email = social_user.email
            EmailAddress.objects.get(email=social_email)

        # Email does not exist, allauth will handle a new social account
        except EmailAddress.DoesNotExist:
            return

        # Email exists, redirect to login page
        client_url = settings.MAGNA_URL + '/login?matched-email=true'

        raise ImmediateHttpResponse(redirect(client_url))
