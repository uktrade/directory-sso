from rest_framework.response import Response
from rest_framework.views import APIView

from directory_healthcheck.views import BaseHealthCheckAPIView
from health_check.db.backends import DatabaseBackend

from conf.signature import SignatureCheckPermission
import core.mixins


class PingAPIView(core.mixins.NoIndexMixin, APIView):

    permission_classes = (SignatureCheckPermission, )
    http_method_names = ("get", )

    def get(self, request, *args, **kwargs):
        return Response(status=200)


class DatabaseAPIView(core.mixins.NoIndexMixin, BaseHealthCheckAPIView):
    def create_service_checker(self):
        return DatabaseBackend()
