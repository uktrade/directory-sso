from django.http import Http404
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveAPIView, get_object_or_404
)
from config.signature import SignatureCheckPermission
from sso.user import models


class UserByEmailAPIView(RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]
    queryset = models.User.objects.all()
    lookup_field = 'email'

    def get(self, request, email, **kwargs):
        user = get_object_or_404(models.User, email=email)
        if user:
            response_data = {
                "sso_id": user.id,
                "is_verified": user.is_active
            }
            return Response(response_data)
        else:
            raise Http404()
