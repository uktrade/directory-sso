from datetime import datetime

from rest_framework.generics import (
    RetrieveAPIView, get_object_or_404, ListAPIView
)
from rest_framework.response import Response
from rest_framework import status

from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError

from sso.api import filters
from config.signature import SignatureCheckPermission
from sso.user.serializers import UserSerializer, LastLoginSerializer
from sso.user.models import User
from sso.user.helpers import UserCache


class SessionUserAPIView(RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    serializer_class = UserSerializer
    lookup_field = 'session_key'

    def get_queryset(self):
        utcnow = datetime.utcnow()
        return Session.objects.filter(expire_date__gt=utcnow)

    def get_object(self):
        session_key = self.request.query_params.get('session_key')

        user_details = UserCache.get(session_key=session_key)
        if user_details:
            return User(email=user_details['email'], id=user_details['id'])

        queryset = self.get_queryset()
        session = get_object_or_404(queryset, session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = get_object_or_404(User, pk=user_id)
        UserCache.set(user=user, session=session)
        return user


class LastLoginAPIView(ListAPIView):
    authentication_classes = []
    filter_class = filters.LastLoginFilter
    permission_classes = [SignatureCheckPermission]
    queryset = User.objects.exclude(last_login__isnull=True)
    serializer_class = LastLoginSerializer

    def handle_exception(self, exception):
        if isinstance(exception, ValidationError):
            return Response(
                exception.message_dict, status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exception)
