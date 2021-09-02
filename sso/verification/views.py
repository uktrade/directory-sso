from allauth.account.models import EmailAddress
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from ratelimit.decorators import ratelimit
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
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


class VerificationTokenRetrieveAPIView(RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]

    def get(self):
        token = helpers.verification_token.make_token(self.request.user.email)

        return Response(status=200, data={'token': token})


class VerifyVerificationCodeAPIView(GenericAPIView):
    serializer_class = serializers.CheckVerificationCodeSerializer
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []

    def get_email(self, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            email_obj = EmailAddress.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, EmailAddress.DoesNotExist):
            email_obj = None

        if email_obj is not None and helpers.verification_token.check_token(email_obj, token):
            return email_obj.email

    def get_object(self):
        uidb64 = self.request.data.get('uidb64')
        token = self.request.data.get('token')

        if uidb64 and token:
            email = self.get_email(uidb64, token)
        else:
            email = self.request.data['email']

        return get_object_or_404(models.VerificationCode.objects.all(), user__email__iexact=email)

    @method_decorator(ratelimit(key='post:email', rate='12/m', method='POST', block=True))
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
