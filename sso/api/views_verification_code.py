from rest_framework.generics import CreateAPIView

from sso.verification.serializers import VerificationCodeSerializer


class ValidationCodeCreateAPIView(CreateAPIView):
    serializer_class = VerificationCodeSerializer
