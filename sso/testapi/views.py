from django.conf import settings
from django.http import HttpResponseNotFound
from rest_framework.generics import (
    get_object_or_404,
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView
)
from rest_framework.response import Response

from conf.signature import SignatureCheckPermission
from sso.user import models


class UserByEmailAPIView(RetrieveAPIView, DestroyAPIView, UpdateAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    queryset = models.User.objects.all()
    lookup_field = 'email'
    http_method_names = ('get', 'delete', 'patch')

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_FLAGS['TEST_API_ON']:
            return HttpResponseNotFound()
        return super().dispatch(*args, **kwargs)

    def get_user(self, **kwargs):
        email = kwargs['email']
        return get_object_or_404(models.User, email=email)

    def get(self, request, **kwargs):
        user = self.get_user(**kwargs)
        response_data = {
            'sso_id': user.id,
            'is_verified': user.is_active
        }
        return Response(response_data)

    def delete(self, request, **kwargs):
        self.get_user(**kwargs).delete()
        return Response(status=204)

    def patch(self, request, *args, **kwargs):
        user = self.get_user(**kwargs)
        is_verified = request.data['is_verified']
        user.emailaddress_set.update_or_create(
            email=user.email,
            defaults={
                'verified': is_verified,
                'user_id': user.id,
                'primary': True
            }
        )
        return Response(status=204)
