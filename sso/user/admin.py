import csv
import datetime

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import TemplateView


from sso.user.models import User
from api_client import api_client



class ExopsNotFabEmailsList(TemplateView):
    template_name = 'admin/user/exops-not-fab-list.html'


    def get_fab_user_ids(self):
        response = api_client.supplier.list_supplier_sso_ids()
        response.raise_for_status()
        return response.json()

    def get_context_data(self):
        fab_user_ids = self.get_fab_user_ids()
        queryset = User.objects.exclude(pk__in=fab_user_ids)
        return {
            'emails': queryset.values_list('email', flat=True)
        }


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    search_fields = ('email', )
    readonly_fields = ('created', 'modified',)
    actions = ['download_csv']

    csv_excluded_fields = (
        'password', 'refreshtoken', 'socialaccount', 'logentry', 'grant',
        'groups', 'accesstoken', 'emailaddress', 'user_permissions'
    )

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            url(
                r'^exops-not-fab-emails/$',
                self.admin_site.admin_view(
                    ExopsNotFabEmailsList.as_view()
                ),
                name="exops-not-fab-emails-list"
            ),
        ]
        return additional_urls + urls

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
