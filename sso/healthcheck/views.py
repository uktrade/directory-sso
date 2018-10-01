from directory_healthcheck.views import BaseHealthCheckAPIView
from health_check.db.backends import DatabaseBackend

import core.mixins


class DatabaseAPIView(core.mixins.NoIndexMixin, BaseHealthCheckAPIView):
    def create_service_checker(self):
        return DatabaseBackend()
