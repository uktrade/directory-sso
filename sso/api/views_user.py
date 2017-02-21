from django.contrib.sessions.models import Session
from django.utils import timezone

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

    def get_queryset(self):
        """Excludes users who are currently logged in"""
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())

        active_user_ids = []
        for session in active_sessions:
            data = session.get_decoded()
            active_user_ids.append(data.get('_auth_user_id', None))

        return User.objects.exclude(id__in=active_user_ids)
