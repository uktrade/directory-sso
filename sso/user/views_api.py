from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


from django.db import IntegrityError

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.user import serializers


class UserCreateAPIView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer
    permission_classes = [SignatureCheckPermission]


class UserProfileCreateAPIView(CreateAPIView):
    serializer_class = serializers.CreateUserProfileSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]
    renderer_classes = [JSONRenderer]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)

        except IntegrityError as error:
            if 'already exists' in str(error):
                return Response(status=200)
            else:
                raise

