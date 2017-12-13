from health_check.views import MainView

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils.crypto import constant_time_compare


class HealthCheckAPIView(MainView):

    def has_permission(self):
        return constant_time_compare(
            self.request.GET.get('token'),
            settings.HEALTH_CHECK_TOKEN
        )

    def get(self, *args, **kwargs):
        if not self.has_permission():
            raise PermissionDenied()
        return super().get(*args, **kwargs)
