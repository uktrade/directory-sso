from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.verification import models, serializers


class VerificationCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]


class VerifyVerificationCodeAPIView(GenericAPIView):
    serializer_class = serializers.CheckVerificationCodeSerializer
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []

    def get_object(self):
        return get_object_or_404(
            models.VerificationCode.objects.all(),
            user__email__iexact=self.request.data['email']
        )

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(date_verified=now())
        return Response()
