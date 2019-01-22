from django.utils.timezone import now
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.verification import serializers, models


class VerificationCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]


class VerifyVerificationCodeAPIView(GenericAPIView):
    serializer_class = serializers.CheckVerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def post(self, request, *args, **kwargs):

        verification_code = models.VerificationCode.objects.get(
            user=request.user
        )
        status_code = status.HTTP_200_OK

        if verification_code:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': self.request},
            )
            serializer.is_valid(raise_exception=True)
            verification_code.date_verified = now()
            verification_code.save()
        else:
            status_code = status.HTTP_404_NOT_FOUND

        return Response(
            data={
                "status_code": status_code,
            },
            status=status_code,
        )
