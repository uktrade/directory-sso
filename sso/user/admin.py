import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from sso.user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    search_fields = ('email', )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv']

    csv_excluded_fields = (
        'password',
    )

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

        field_names = sorted([
            field.name for field in User._meta.get_fields()
            if field.name not in self.csv_excluded_fields
        ])

        users = queryset.all().values(*field_names)
        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()

        for user in users:
            writer.writerow(user)

        return response

    download_csv.short_description = (
        "Download CSV report for selected users"
    )
