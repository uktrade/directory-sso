from rest_framework.generics import CreateAPIView

from sso.verification.serializers import ValidationSerializer


class ValidationCreateAPIView(CreateAPIView):
    serializer_class = ValidationSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance

        return instance
