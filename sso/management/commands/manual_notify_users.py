from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from notifications_python_client import NotificationsAPIClient

from sso.user.models import User


class Command(BaseCommand):
    """
    Notify inactive users who have either registered on a particular date but never logged in
    or not logged in since the aforementioned date.

    Usage:
            python manage.py manual_notify_users 14 --date 2018-01-01
            make manage manual_notify_users -- 14 --date 2018-01-01
    """

    DATA_RETENTION_STORAGE_YEARS = 3

    help = 'Notify inactive users of potential account deletion'

    def add_arguments(self, parser):
        parser.add_argument(
            'notification_days',
            type=int,
            help='Number of days of notice to include in the email notification. Possible entries are: 30, 14, 7, 0',
        )
        parser.add_argument(
            '--date',
            type=int,
            help='Date from which to filter inactive user accounts with the format YYYY-MM-DD',
        )

    def handle(self, *args, **options):
        now_date = timezone.now()
        notification_days = options['notification_days']

        if options['date']:
            end_date = now_date
            start_date = timezone.make_aware(
                datetime.strptime(options['date'], "%Y-%m-%d"), timezone=pytz.timezone(settings.TIME_ZONE)
            )
            time_window = relativedelta(start_date, end_date)
        else:
            time_window = relativedelta(years=self.DATA_RETENTION_STORAGE_YEARS)

        date = now_date - time_window

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
                last_login__lte=date,
                inactivity_notification=inactivity_notification,
            )
            |
            # Accounts with no login activity, with creation dated less than or equal year and month provided
            Q(
                last_login__isnull=True,
                created__lte=date,
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
