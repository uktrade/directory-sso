from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from conf.signature import SignatureCheckPermission

from sso.verification import models, serializers


class ValidationCodeCreateAPIView(CreateAPIView):
    serializer_class = serializers.VerificationCodeSerializer
    '#queryset = models.VerificationCode.objects'
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = []
