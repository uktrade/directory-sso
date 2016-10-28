from django.contrib.sessions.models import Session

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from sso.user.serializers import UserSerializer
from sso.user.models import User


class SessionUserAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserSerializer
    lookup_field = 'session_key'

    def get_object(self):
        session_key = self.request.query_params.get('session_key')
        session = Session.objects.get(session_key=session_key)

        session_data = session.get_decoded()

        user_id = session_data.get('_auth_user_id')

        return User.objects.get(pk=user_id)
