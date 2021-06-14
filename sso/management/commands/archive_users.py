import json
from datetime import datetime, timedelta

from directory_api_client import api_client
from directory_forms_api_client.client import forms_api_client
from django.conf import settings
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.models import Q

from sso.user.models import DataRetentionStatistics, User


class Command(MigrateCommand):
    """
    Archive users who's not logged in past three years
    or created three years ago and never logged in
    """

    def handle(self, *args, **options):
        queryset = User.objects.all()
        total_users = queryset.count()
        three_year_old = datetime.now() - timedelta(days=3 * 365)
        company, company_user = 0, 0

        old_users = queryset.filter(
            # last login 3 years old and inactivity_notification=4 means we have sent final notification to user
            Q(last_login__lt=three_year_old, created__lt=three_year_old, inactivity_notification=4)
            |
            # account created 3 years ago but never logged in and inactivity_notification=4
            # means we have sent final notification to user
            Q(last_login__isnull=True, created__lt=three_year_old, inactivity_notification=4)
        )
        total_old_users = old_users.count()
        # Delete related user data in directory-api
        for user in old_users:
            # directory-api data removal
            response = api_client.company.delete_company_by_sso_id(
                sso_id=user.id, request_key=settings.DIRECTORY_API_SECRET
            )
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        f'Something went wrong while deleting {user}'
                        f'(user_id:{user.id}) \'s data in directory-api repo'
                    )
                )
                raise Exception('Something went wrong in directory-api')

            # form-api data removal
            forms_api_response = forms_api_client.delete_submissions(email_address=user.email)
            if forms_api_response.status_code != 204:
                self.stdout.write(
                    self.style.ERROR(
                        f'Something went wrong while deleting {user}'
                        f'(user_id:{user.id}) \'s data in directory-forms-api repo'
                    )
                )
                raise Exception('Something went wrong in directory-forms-api')

            json_response = json.loads(response.content)
            company += int(json_response.get('company_counter', 0))
            company_user += int(json_response.get('company_user_count', 0))

        # Delete sso users
        old_users.delete()
        DataRetentionStatistics.objects.create(
            sso_user=total_old_users,
            company=company,
            company_user=company_user,
        )
        self.stdout.write(self.style.WARNING(f'Total users: {total_users}'))
        self.stdout.write(self.style.WARNING(f'Number of users deleted: {total_old_users}'))
        self.stdout.write(self.style.SUCCESS('Successfully deleted 3 years old users... Good bye!!'))
