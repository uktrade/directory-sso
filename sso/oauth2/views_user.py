from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from oauth2_provider.contrib.rest_framework import TokenHasScope

from sso.user.serializers import UserSerializer


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['profile']
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
