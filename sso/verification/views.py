from datetime import datetime

from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from conf.signature import SignatureCheckPermission

from sso.verification import serializers, models
from core.authentication import SessionAuthentication


class VerificationCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]


class VerifyVerificationCodeAPIView(GenericAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]
    queryset = models.VerificationCode.objects.all()
    http_method_names = ("post",)
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):

        verification_code = models.VerificationCode.objects.get(
            user=request.user
        )
        status_code = status.HTTP_200_OK
        return_msg = 'User verified with code'

        if verification_code:
            serializer = self.serializer_class(
                data=request.data,
                context={'expected_code': verification_code.code},
            )

            serializer.is_valid(raise_exception=True)
            verification_code.verified_date = datetime.utcnow()
            verification_code.save()
        else:
            status_code = status.HTTP_404_NOT_FOUND
            return_msg = 'No verification code found for user'

        return Response(
            data={
                "status_code": status_code,
                "detail": return_msg
            },
            status=status_code,
        )
