import datetime

from allauth.account.models import EmailAddress

from django.core.management.base import BaseCommand
from oauth2_provider.models import AccessToken, Application

from sso.user.models import User


class Command(BaseCommand):
    help = 'Used to create a users for integration tests.'

    def handle(self, *args, **options):
        verified_user = create_verified_integration_test_user()
        create_login_for_token_integration_test_user(verified_user)
        unverified_user = create_unverified_integration_test_user()
        create_login_for_token_integration_test_user(unverified_user)


def create_verified_integration_test_user():
    user = User.objects.create_user(
        email='verified@example.com',
        password='passwordpassword'
    )
    EmailAddress.objects.create(
        user=user,
        email='verified@example.com',
        verified=True,
        primary=True,
    )
    return user


def create_unverified_integration_test_user():
    user = User.objects.create_user(
        email='unverified@example.com',
        password='passwordpassword'
    )
    EmailAddress.objects.create(
        user=user,
        email='unverified@example.com',
        verified=False,
        primary=True,
    )
    return user


def create_application(user):
    return Application.objects.create(
        user=user,
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        name='Test client'
    )


def create_login_for_token_integration_test_user(user):
    AccessToken.objects.create(
        user=user,
        application=create_application(user),
        token='1234567890',
        expires=datetime.datetime.now() + datetime.timedelta(days=1000),
        scope='profile'
    )
