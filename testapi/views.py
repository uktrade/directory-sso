from django.http import Http404
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveAPIView, get_object_or_404
)

from config import settings
from sso.user import models
from testapi.permissions import IsAuthenticatedTestAPI


class UserByEmailAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticatedTestAPI]
    queryset = models.User.objects.all()
    lookup_field = 'email'
    http_method_names = ("get", )

    def dispatch(self, *args, **kwargs):
        if not settings.TEST_API_ENABLE:
            raise Http404()
        return super().dispatch(*args, **kwargs)

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
