from random import randint
from uuid import uuid4

from django.conf import settings
from django.db.utils import IntegrityError
from django.http import HttpResponseNotFound
from django.shortcuts import get_list_or_404
from rest_framework.generics import DestroyAPIView, RetrieveAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response

import core.mixins
from conf.signature import SignatureCheckPermission
from sso.user import models


class UserByEmailAPIView(core.mixins.NoIndexMixin, RetrieveAPIView, DestroyAPIView, UpdateAPIView):
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
        response_data = {'sso_id': user.id, 'is_verified': user.is_active}
        return Response(response_data)

    def delete(self, request, **kwargs):
        self.get_user(**kwargs).delete()
        return Response(status=204)

    def patch(self, request, *args, **kwargs):
        user = self.get_user(**kwargs)
        is_verified = request.data['is_verified']
        user.emailaddress_set.update_or_create(
            email=user.email, defaults={'verified': is_verified, 'user_id': user.id, 'primary': True}
        )
        return Response(status=204)


class TestUsersAPIView(core.mixins.NoIndexMixin, DestroyAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    queryset = models.User.objects.all()
    http_method_names = ['delete', 'post']

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_FLAGS['TEST_API_ON']:
            return HttpResponseNotFound()
        return super().dispatch(*args, **kwargs)

    def delete(self, request, **kwargs):
        domain_pattern = str.replace(settings.FEATURE_FLAGS["TEST_API_EMAIL_DOMAIN"], ".", "\\.")
        test_users = get_list_or_404(
            models.User,
            email__regex=rf'^test\+(.*)@{domain_pattern}',
        )
        for user in test_users:
            user.delete()
        return Response(status=204)

    def post(self, request, **kwargs):
        try:
            domain = settings.FEATURE_FLAGS["TEST_API_EMAIL_DOMAIN"]
            user = models.User.objects.create(
                email=request.data.get('email', f'test+{str(uuid4()).replace("-", "")}@{domain}'),
            )
            user.save()
            profile = models.UserProfile.objects.create(
                user=user,
                first_name=request.data.get('first_name', 'Automated'),
                last_name=request.data.get('last_name', 'Test'),
                job_title=request.data.get('job_title', 'AUTOMATED TESTS'),
                mobile_phone_number=request.data.get('mobile_phone_number', randint(1000000000000, 9999999999999)),
            )
            profile.save()
            user = profile.user
            user.set_password(request.data.get('password', 'password'))
            user.save()
            # don't use default UserSerializer as we want flat structure in response
            data = {
                'email': user.email,
                'password': request.data.get('password', 'password'),
                'id': user.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'job_title': profile.job_title,
                'mobile_phone_number': profile.mobile_phone_number,
            }
            return Response(data=data)
        except IntegrityError as ex:
            data = {'error': str(ex)}
            return Response(status=400, data=data)
