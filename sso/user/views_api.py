from rest_framework.generics import CreateAPIView

from conf.signature import SignatureCheckPermission
from .serializers import CreateUserSerializer


class UserCreateAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [SignatureCheckPermission]
