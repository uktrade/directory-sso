from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import Http404
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.verification import serializers


class VerificationCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]


class VerifyVerificationCodeAPIView(GenericAPIView):
    serializer_class = serializers.CheckVerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def get_object(self):
        try:
            return self.request.user.verification_code
        except ObjectDoesNotExist:
            raise Http404()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(date_verified=now())
        return Response()
