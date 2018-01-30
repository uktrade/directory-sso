from rest_framework.generics import (
    RetrieveAPIView, get_object_or_404
)
from config.signature import SignatureCheckPermission
from sso.user import models


class UserByEmailAPIView(RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]
    queryset = models.User.objects.all()
    authentication_classes = []
    serializer_class = []
    lookup_field = 'email'

    def get(self, request, email, **kwargs):
        email = self.request.query_params.get('email')
        user = get_object_or_404(models.User, email=email)
        return user
