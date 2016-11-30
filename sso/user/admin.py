from django.contrib import admin

from sso.user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)
