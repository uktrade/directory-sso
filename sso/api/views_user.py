from django.contrib.sessions.models import Session

from rest_framework.generics import (
    RetrieveAPIView, get_object_or_404, ListAPIView)

from sso.api.permissions import APIClientPermission
from sso.user.serializers import UserSerializer, LastLoginSerializer
from sso.user.models import User


class SessionUserAPIView(RetrieveAPIView):
    permission_classes = [APIClientPermission]
    authentication_classes = []
    serializer_class = UserSerializer
    lookup_field = 'session_key'

    def get_object(self):
        session_key = self.request.query_params.get('session_key')
        session = get_object_or_404(Session, session_key=session_key)

        session_data = session.get_decoded()

        user_id = session_data.get('_auth_user_id')

        return get_object_or_404(User, pk=user_id)


class LastLoginAPIView(ListAPIView):
    permission_classes = [APIClientPermission]
    authentication_classes = []
    serializer_class = LastLoginSerializer
    queryset = User.objects
