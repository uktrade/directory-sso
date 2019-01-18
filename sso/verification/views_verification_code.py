from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from conf.signature import SignatureCheckPermission

from sso.verification import serializers


class VerificationCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = []
