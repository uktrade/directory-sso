from django.conf import settings
from django.http import HttpResponseNotFound
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from config.signature import SignatureCheckPermission
from sso.user import models


class UserByEmailAPIView(RetrieveAPIView, DestroyAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    queryset = models.User.objects.all()
    lookup_field = 'email'
    http_method_names = ('get', 'delete')

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_TEST_API_ENABLE:
            return HttpResponseNotFound()
        return super().dispatch(*args, **kwargs)

    def get_user(self, email):
        return get_object_or_404(models.User, email=email)

    def get(self, request, **kwargs):
        email = kwargs['email']
        user = self.get_user(email)
        response_data = {
            'sso_id': user.id,
            'is_verified': user.is_active
        }
        return Response(response_data)

    def delete(self, request, **kwargs):
        email = kwargs['email']
        self.get_user(email).delete()
        return Response(status=204)
