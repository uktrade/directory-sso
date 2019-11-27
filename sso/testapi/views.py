from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import get_list_or_404
from rest_framework.generics import (
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

import core.mixins
from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.user import models


class UserByEmailAPIView(
    core.mixins.NoIndexMixin, RetrieveAPIView, DestroyAPIView, UpdateAPIView
):
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


class TestUsersAPIView(core.mixins.NoIndexMixin, DestroyAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    queryset = models.User.objects.all()
    http_method_names = 'delete'

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_FLAGS['TEST_API_ON']:
            return HttpResponseNotFound()
        return super().dispatch(*args, **kwargs)

    def delete(self, request, **kwargs):
        test_users = get_list_or_404(
            models.User,
            email__regex=r'^test\+(.*)@directory\.uktrade\.io',
        )
        for user in test_users:
            user.delete()
        return Response(status=204)
