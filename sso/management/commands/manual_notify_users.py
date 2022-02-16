from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from notifications_python_client import NotificationsAPIClient

from sso.user.models import User


class Command(BaseCommand):
    """
    Notify inactive users who have either registered on a particular date but never logged in
    or not logged in since the aforementioned date.

    Usage:
            python manage.py manual_notify_users 14 --from-year 2018 --from-month 1
            make manage manual_notify_users -- 14 --from-year 2018 --from-month 1
    """

    DATA_RETENTION_STORAGE_YEARS = 3

    help = 'Notify inactive users of potential account deletion'

    def add_arguments(self, parser):
        current_datetime = datetime.now()
        current_year = current_datetime.year
        current_month = current_datetime.month

        parser.add_argument(
            'notification_days',
            type=int,
            help='Number of days of notice to include in the email notification. Possible entries are: 30, 14, 7, 0',
        )
        parser.add_argument(
            '--from-year',
            type=int,
            dest='from_year',
            default=(current_year - self.DATA_RETENTION_STORAGE_YEARS),
            help='Year from which to filter inactive user accounts. Defaults to exactly three years back',
        )
        parser.add_argument(
            '--from-month',
            type=int,
            dest='from_month',
            default=current_month,
            help='Month from which to filter inactive user accounts. Defaults to current month',
        )

    def handle(self, *args, **options):
        notification_days = options['notification_days']
        from_year = options['from_year']
        from_month = options['from_month']

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

        inactive_users = queryset.filter(
            # Accounts with last login dated less than or equal year and month provided
            Q(
                last_login__year__lte=from_year,
                last_login__month__lte=from_month,
                inactivity_notification=inactivity_notification,
            )
            |
            # Accounts with no login activity, with creation dated less than or equal year and month provided
            Q(
                last_login__isnull=True,
                created__year__lte=from_year,
                created__month__lte=from_month,
                inactivity_notification=inactivity_notification,
            )
        )
        # Notify users about deletion
        for user in inactive_users:
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

        self.stdout.write(self.style.SUCCESS('Notification sent'))
