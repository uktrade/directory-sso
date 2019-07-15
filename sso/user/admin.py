import csv
import datetime

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

from sso.user.models import User, UserProfile
from directory_api_external.client import api_client


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    search_fields = ('email',)
    readonly_fields = ('created', 'modified',)
    list_display = ('email', 'is_superuser', 'is_staff')
    exclude = ('password',)
    actions = [
        'download_csv',
        'download_csv_exops_not_fab',
        'download_email_verification_links',
        'download_password_reset_links'
    ]

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

        fieldnames = sorted(
            [field.name for field in self.model._meta.get_fields()
             if field.name not in self.csv_excluded_fields]
        )

        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()
        for obj in queryset.all().values(*fieldnames):
            writer.writerow(obj)

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

    @staticmethod
    def generate_csv_response_for_list_of_dicts(filename_prefix, data, fields):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="{prefix}_{timestamp}.csv"'.format(
                prefix=filename_prefix,
                timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            )
        )
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for element in data:
            writer.writerow(element)

        return response

    def download_email_verification_links(self, request, queryset):
        email_verification_links = [
            {
                'email': user.email,
                'email_verification_link': user.get_email_verification_link()
            } for user in queryset
        ]

        return self.generate_csv_response_for_list_of_dicts(
            filename_prefix='sso_email_verification_links',
            data=email_verification_links,
            fields=['email', 'email_verification_link']
        )

    download_email_verification_links.short_description = (
        "Download email verification links for selected users"
    )

    def download_password_reset_links(self, request, queryset):
        password_reset_links = [
            {
                'email': user.email,
                'password_reset_link': user.get_password_reset_link()
            } for user in queryset
        ]

        return self.generate_csv_response_for_list_of_dicts(
            filename_prefix='sso_password_reset_links',
            data=password_reset_links,
            fields=['email', 'password_reset_link']
        )

    download_password_reset_links.short_description = (
        "Download password reset links for selected users"
    )
