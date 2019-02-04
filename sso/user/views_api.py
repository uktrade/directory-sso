from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateUserSerializer, CreateUserProfileSerializer

from django.contrib.auth import login

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication


class UserCreateAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [SignatureCheckPermission]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        login(
            request=self.request,
            user=serializer.instance,
            backend='django.contrib.auth.backends.ModelBackend',
        )


class UserProfileCreateAPIView(CreateAPIView):
    serializer_class = CreateUserProfileSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]
