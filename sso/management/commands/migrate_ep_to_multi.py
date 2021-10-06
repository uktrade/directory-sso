import json
from datetime import datetime, timedelta

from directory_api_client import api_client
from directory_forms_api_client.client import forms_api_client
from django.conf import settings
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.models import Q

from sso.user.models import DataRetentionStatistics, User
from django.contrib.sessions.models import Session
from django.utils import timezone


class Command(MigrateCommand):
    """
    Migrate existing product and market data to the new multi-product/market model.
    """

    def handle(self, *args, **options):
        all_users = User.objects.all()
        user_id_and_session_key = {}

        # Active sessions.
        sessions = Session.objects.filter(expire_date__gt=timezone.now())
        for session in sessions:
            user_session_id = session.get_decoded().get('_auth_user_id')
            user_id_and_session_key = {user_session_id: session.session_key}

        for user in all_users:
            try:
                session_key = user_id_and_session_key[str(user.id)]
                response = api_client.exportplan.detail_list(sso_session_id=session_key)

                if response.status_code != 200:
                    self.stdout.write(self.style.ERROR(f'Something went wrong while pulling exportplan.'))
                    raise Exception('Something went wrong in directory-api')

                json_response = json.loads(response.content)
                print(json_response)
            except KeyError:
                pass

        # self.stdout.write(self.style.WARNING(f'Total users: {total_users}'))
        # self.stdout.write(self.style.WARNING(f'Number of users deleted: {total_old_users}'))
        # self.stdout.write(self.style.SUCCESS('Successfully deleted 3 years old users... Good bye!!'))