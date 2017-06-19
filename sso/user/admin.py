import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from sso.user.models import User

from api_client import api_client


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    search_fields = ('email', )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv']

    csv_excluded_fields = (
        'password', 'refreshtoken', 'socialaccount', 'logentry', 'grant',
        'groups', 'accesstoken', 'emailaddress', 'user_permissions'
    )

    def get_fab_user_ids(self):
        response = api_client.supplier.list_supplier_sso_ids()
        response.raise_for_status()
        return response.json()

    def download_csv(self, request, queryset):
        """
        Generates CSV report of selected users.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="sso_users_{}.csv"'.format(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            )
        )

        database_field_names = [
            field.name for field in User._meta.get_fields()
            if field.name not in self.csv_excluded_fields
        ]
        computed_field_names = ['is_exops_user', 'is_fab_user']
        csv_fieldnames = sorted(database_field_names+computed_field_names)

        users = queryset.all().values(*database_field_names)
        fab_user_ids = self.get_fab_user_ids()
        writer = csv.DictWriter(response, fieldnames=csv_fieldnames)
        writer.writeheader()

        for user in users:
            writer.writerow({
                'is_fab_user': user['id'] in fab_user_ids,
                'is_exops_user': False,
                **user
            })

        return response

    download_csv.short_description = (
        "Download CSV report for selected users"
    )
