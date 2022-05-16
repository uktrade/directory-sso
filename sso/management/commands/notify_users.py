from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.commands.migrate import Command as MigrateCommand
from notifications_python_client import NotificationsAPIClient

from sso.user.models import User


class Command(MigrateCommand):
    """
    Archive users who's not logged in past three years
    or created three years ago and never logged in
    """

    def handle(self, *args, **options):
        queryset = User.inactive

        today = datetime.now()

        notification_note = {
            0: 'in the next 30 days',
            1: 'in the next 14 days',
            2: 'in the next 7 days',
            3: 'today',
        }

        notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
        template_id = settings.GOV_NOTIFY_DATA_RETENTION_NOTIFICATION_TEMPLATE_ID

        # This remindar batch refer to notification batch of 30, 14, 7 and 0 days
        # So notification counter align as 1 -> 30 days, 2->14 days, 3 -> 7 days 4 -> 0 day
        # also same value as counter will be saved in db as inactivity_notification
        # so this is to track notification and avoid sending multiple notification
        notification_remindar = {
            0: None,
            1: 14,
            2: 7,
            3: 7,
        }

        for notification_counter, note in notification_note.items():
            queryset = queryset.filter(inactivity_notification=notification_counter)
            if notification_remindar.get(notification_counter):
                old_users = queryset.filter(
                    inactivity_notification_sent__lte=today
                    - timedelta(days=notification_remindar.get(notification_counter)),  # noqa
                )
            # Notify user about deletion
            for user in old_users:
                response = notifications_client.send_email_notification(
                    email_address=user.email,
                    template_id=template_id,
                    personalisation={'day_variation': note},
                )
                if hasattr(response, 'status_code') and response.status_code in [400, 403, 404, 429, 500]:
                    raise Exception(f'Something went wrong in GOV notification service while notifying {user}')
                else:
                    user.inactivity_notification += 1
                    user.inactivity_notification_sent = today
                    user.save()

        self.stdout.write(self.style.SUCCESS('Notification sent!!'))
