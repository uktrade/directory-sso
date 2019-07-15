from django.contrib import admin

from sso.verification.models import VerificationCode


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified', 'date_verified', 'code', 'user')
    list_display = ('user', 'date_verified', )

