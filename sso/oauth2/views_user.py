from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from oauth2_provider.contrib.rest_framework import TokenHasScope
import oauth2_provider.views

import core.mixins
from sso.user.serializers import UserSerializer


class UserRetrieveAPIView(core.mixins.NoIndexMixin, RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['profile']
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class AuthorizationView(
    core.mixins.NoIndexMixin, oauth2_provider.views.AuthorizationView
):
    pass


class TokenView(core.mixins.NoIndexMixin, oauth2_provider.views.TokenView):
    pass


class RevokeTokenView(
    core.mixins.NoIndexMixin, oauth2_provider.views.RevokeTokenView
):
    pass
