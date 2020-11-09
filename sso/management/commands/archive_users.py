from datetime import datetime, timedelta

from django.core.management.commands.migrate import Command as MigrateCommand
from django.conf import settings
from django.db.models import Q

from sso.user.models import User
from directory_api_client import api_client


class Command(MigrateCommand):
    """
    Archive users who's not logged in past three years
    or created three years ago and never logged in
    """

    def handle(self, *args, **options):
        queryset = User.objects.all()
        total_users = queryset.count()
        three_year_old = datetime.now() - timedelta(days=3*365)

        old_users = queryset.filter(
            # last login 3 years old
            Q(
                last_login__lt=three_year_old,
                created__lt=three_year_old
            ) |
            # account created 3 years ago but never logged in
            Q(
                last_login__isnull=True,
                created__lt=three_year_old
            )
        )
        total_old_users = old_users.count()

        # Delete related user data in directory-api
        for user in old_users:
            response = api_client.company.delete_company_by_sso_id(
                sso_id=user.id,
                request_key=settings.DIRECTORY_API_SECRET
            )
            if response.status_code != 204:
                self.stdout.write(
                    self.style.ERROR(f'Something went wrong while deleting {user}'
                                     f'(user_id:{user.id}) \'s data in directory-api repo')
                )
                raise Exception('Something went wrong in directory-api')

        # Delete sso users
        old_users.delete()

        self.stdout.write(self.style.WARNING(f'Total users: {total_users}'))
        self.stdout.write(self.style.WARNING(f'Number of users deleted: {total_old_users}'))
        self.stdout.write(self.style.SUCCESS('Successfully deleted 3 years old users... Good bye!!'))
