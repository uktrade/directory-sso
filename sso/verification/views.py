from allauth.account.models import EmailAddress
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from conf.signature import SignatureCheckPermission
from sso.verification import helpers, models, serializers


class RegenerateCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.RegenerateCodeSerializer
    permission_classes = [SignatureCheckPermission]

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data={
                'created': now(),
                'code': helpers.generate_verification_code(),
            },
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    def get_object(self):
        return get_object_or_404(models.VerificationCode.objects.all(), user__email__iexact=self.request.data['email'])


class VerifyVerificationCodeAPIView(GenericAPIView):
    serializer_class = serializers.CheckVerificationCodeSerializer
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []

    def get_object(self):
        return get_object_or_404(models.VerificationCode.objects.all(), user__email__iexact=self.request.data['email'])

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(date_verified=now())

        EmailAddress.objects.get_or_create(
            user=instance.user,
            verified=True,
            email=instance.user.email,
            primary=True,
        )

        login(
            request=self.request,
            user=instance.user,
            backend='django.contrib.auth.backends.ModelBackend',
        )
        return Response()
