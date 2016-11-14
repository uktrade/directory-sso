from allauth.account.models import EmailAddress

from django.core.management.base import BaseCommand

from sso.user.models import User


class Command(BaseCommand):
    help = 'Used to create a users for integration tests.'

    def handle(self, *args, **options):
        create_verified_integration_test_user()


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
