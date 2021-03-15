from datetime import datetime, timedelta, timezone

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

    def handle(self, *args, **options):
        queryset = User.objects.all()

        today = datetime.now(timezone.utc)
        three_year_old = today - timedelta(days=3 * 365)
        thirty_day_notification = three_year_old - timedelta(days=30)
        forty_day_notification = three_year_old - timedelta(days=14)
        seven_day_notification = three_year_old - timedelta(days=7)
        zero_day_notification = three_year_old - timedelta(days=0)

        notification_batch = {
            thirty_day_notification.date(): 'in the next 30 days',
            forty_day_notification.date(): 'in the next 14 days',
            seven_day_notification.date(): 'in the next 7 days',
            zero_day_notification.date(): 'today',
        }

        notifications_client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
        template_id = settings.GOV_NOTIFY_DATA_RETENTION_NOTIFICATION_TEMPLATE_ID

        for notification_date, note in notification_batch.items():
            old_users = queryset.filter(
                # last login 3 years old
                Q(
                    last_login__year=notification_date.year,
                    last_login__month=notification_date.month,
                    last_login__day=notification_date.day,
                    created__lt=notification_date,
                )
                |
                # account created 3 years ago but never logged in
                Q(
                    last_login__isnull=True,
                    created__year=notification_date.year,
                    created__month=notification_date.month,
                    created__day=notification_date.day,
                )
            )

            # Notify user about deletion
            for user in old_users:
                response = notifications_client.send_email_notification(
                    email_address=user.email,
                    template_id=template_id,
                    personalisation={'day_variation': note},
                )

                if response.status_code != 201:
                    self.stdout.write(self.style.ERROR(f'Something went wrong while sending notification to {user}'))

            self.stdout.write(self.style.SUCCESS('Notification sent!!'))
