from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_filters.views import FilterMixin
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from conf.signature import SignatureCheckPermission
from sso.api import filters
from sso.user import models, serializers


class GetUserBySessionKeyMixin:
    def get_session_queryset(self):
        return Session.objects.filter(expire_date__gt=timezone.now())

    def get_session_key_user(self, session_key):
        queryset = self.get_session_queryset()
        session = get_object_or_404(queryset, session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        return get_object_or_404(models.User.objects.select_related('user_profile'), pk=user_id)


class SessionUserAPIView(GetUserBySessionKeyMixin, RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    serializer_class = serializers.UserSerializer
    lookup_field = 'session_key'

    def get_object(self):
        session_key = self.request.query_params.get('session_key')
        return self.get_session_key_user(session_key)


class LastLoginAPIView(FilterMixin, ListAPIView):
    authentication_classes = []
    filterset_class = filters.LastLoginFilter
    permission_classes = [SignatureCheckPermission]
    queryset = models.User.objects.exclude(last_login__isnull=True)
    serializer_class = serializers.LastLoginSerializer
    strict = True

    def handle_exception(self, exception):
        if isinstance(exception, ValidationError):
            return Response(exception.message_dict, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exception, TypeError):
            return Response(str(exception), status=status.HTTP_400_BAD_REQUEST)
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
