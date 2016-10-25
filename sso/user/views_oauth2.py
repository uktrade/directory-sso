from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from oauth2_provider.ext.rest_framework import TokenHasScope

from sso.user.models import User
from sso.user.serializers import UserSerializer


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['profile']
    serializer_class = UserSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)
