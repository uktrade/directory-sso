from django.contrib.sessions.models import Session

from rest_framework.generics import RetrieveAPIView, get_object_or_404

from sso.api.permissions import APIClientPermission
from sso.user.serializers import UserSerializer
from sso.user.models import User


class SessionUserAPIView(RetrieveAPIView):
    permission_classes = [APIClientPermission]
    authentication_classes = []
    serializer_class = UserSerializer
    lookup_field = 'session_key'

    def get_object(self):
        session_key = self.request.query_params.get('session_key')
        session = get_object_or_404(
            queryset=Session.objects.filter(session_key=session_key),
            session_key=session_key
        )

        session_data = session.get_decoded()

        user_id = session_data.get('_auth_user_id')

        return get_object_or_404(
            queryset=User.objects.filter(pk=user_id),
            pk=user_id
        )
