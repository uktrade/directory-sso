import csv
import datetime

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

from sso.user.models import User

from sso.user.utils import api_client


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    search_fields = ('email', )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv', 'download_csv_exops_not_fab']

    csv_excluded_fields = (
        'password', 'oauth2_provider_refreshtoken',
        'socialaccount', 'logentry', 'oauth2_provider_grant',
        'groups', 'oauth2_provider_accesstoken', 'emailaddress',
        'user_permissions', 'failed_login_attempts'
    )

    @staticmethod
    def get_fab_user_ids():
        response = api_client.supplier.list_supplier_sso_ids()
        response.raise_for_status()
        return response.json()

    def get_user_database_field_names(self):
        return sorted([
            field.name for field in User._meta.get_fields()
            if field.name not in self.csv_excluded_fields
        ])

    def generate_csv_for_queryset(self, queryset, filename_prefix):
        """
        Generates CSV report of selected users.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="{prefix}_{timestamp}.csv"'.format(
                prefix=filename_prefix,
                timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            )
        )

        field_names = self.get_user_database_field_names()

        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()
        for user in queryset.all().values(*field_names):
            writer.writerow(user)

        return response

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected users.
        """

        return self.generate_csv_for_queryset(
            queryset=queryset, filename_prefix='sso_users'
        )

    def download_csv_exops_not_fab(self, request, queryset):
        """
        Generates CSV report of all users that have ExOpps accounts but not FAB
        """

        client_id = settings.EXOPS_APPLICATION_CLIENT_ID
        queryset = (
            queryset
            .exclude(pk__in=self.get_fab_user_ids())
            .filter(
                oauth2_provider_accesstoken__application__client_id=client_id
            )
            .distinct()
        )
        return self.generate_csv_for_queryset(
            queryset=queryset, filename_prefix='exops_not_fab_sso_users'
        )

    download_csv.short_description = (
        "Download CSV report for selected users"
    )
    download_csv_exops_not_fab.short_description = (
        "Download CSV report for selected users that have an ExOpps account "
        "but not a FAB account"
    )
