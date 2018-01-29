from datetime import datetime

from rest_framework.generics import (
    RetrieveAPIView, get_object_or_404, ListAPIView
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError

from sso.api import filters
from config.signature import SignatureCheckPermission
from sso.user import models, serializers
from sso.user.helpers import UserCache


class GetUserBySessionKeyMixin:
    def get_session_queryset(self):
        utcnow = datetime.utcnow()
        return Session.objects.filter(expire_date__gt=utcnow)

    def get_session_key_user(self, session_key):

        if settings.FEATURE_CACHE_ENABLED:
            user_details = UserCache.get(session_key=session_key)
            if user_details:
                return models.User(
                    email=user_details['email'], id=user_details['id']
                )

        queryset = self.get_session_queryset()
        session = get_object_or_404(queryset, session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = get_object_or_404(models.User, pk=user_id)

        if settings.FEATURE_CACHE_ENABLED:
            UserCache.set(user=user, session=session)

        return user


class SessionUserAPIView(GetUserBySessionKeyMixin, RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    serializer_class = serializers.UserSerializer
    lookup_field = 'session_key'

    def get_object(self):
        session_key = self.request.query_params.get('session_key')
        return self.get_session_key_user(session_key)


class LastLoginAPIView(ListAPIView):
    authentication_classes = []
    filter_class = filters.LastLoginFilter
    permission_classes = [SignatureCheckPermission]
    queryset = models.User.objects.exclude(last_login__isnull=True)
    serializer_class = serializers.LastLoginSerializer

    def handle_exception(self, exception):
        if isinstance(exception, ValidationError):
            return Response(
                exception.message_dict, status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exception)


class PasswordCheckAPIView(GetUserBySessionKeyMixin, APIView):
    authentication_classes = []
    permission_classes = [SignatureCheckPermission]

    serializer_class = serializers.PasswordCheckSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_key = serializer.validated_data['session_key']
        user = self.get_session_key_user(session_key)
        if user.check_password(serializer.validated_data['password']):
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(status=status_code)
