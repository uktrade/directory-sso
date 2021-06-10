from django.conf import settings
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.models import Q
from notifications_python_client import NotificationsAPIClient

from sso.user.models import User


class Command(MigrateCommand):
    """
    Archive users who's not logged in past three years
    or created three years ago and never logged in
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'notification_days',
            type=int,
            help='Notification days you would like to send, possibly entry 30, 14, 7, 0',
        )

    def handle(self, *args, **options):

        notification_days = options['notification_days']
        queryset = User.objects.all()

        notification_batch = {
            30: 0,
            14: 1,
            7: 2,
            0: 3,
        }

        notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
        template_id = settings.GOV_NOTIFY_DATA_RETENTION_NOTIFICATION_TEMPLATE_ID

        inactivity_notification = notification_batch.get(notification_days, 30)

        old_users = queryset.filter(
            # last login 3 years old
            Q(
                last_login__year__lte=2018,
                last_login__month__lte=6,
                inactivity_notification=inactivity_notification,
            )
            |
            # account created 3 years ago but never logged in
            Q(
                last_login__isnull=True,
                created__year__lte=2018,
                created__month__lte=6,
                inactivity_notification=inactivity_notification,
            )
        )
        # Notify user about deletion
        for user in old_users:

            if user.inactivity_notification >= 4:
                continue

            note = (f'in the next {notification_days} days',)
            if notification_days == 0:
                note = 'today'

            response = notifications_client.send_email_notification(
                email_address=user.email,
                template_id=template_id,
                personalisation={'day_variation': note},
            )

            if hasattr(response, 'status_code') and response.status_code in [400, 403, 404, 429, 500]:
                raise Exception(f'Something went wrong in GOV notification service while notifying {user}')
            else:
                user.inactivity_notification += 1
                user.save()

        self.stdout.write(self.style.SUCCESS('Notification sent!!'))
