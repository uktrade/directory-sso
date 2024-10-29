from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from sso.user import serializers
from sso.user.models import UserProfile



class CacheView(GenericAPIView):
    '''
    Temporary view to help develop and test caching

    This view is only wired up to a url if settings.DEBUG == True
    '''

    permission_classes = []
    authentication_classes = []
    serializer_class = serializers.UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.all()

    def get_object(self):
        return self.get_queryset().last()

    def get(self, request):
        data = {}
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            data = serializer.data
        except ObjectDoesNotExist:
            pass
        return Response(status=200, data=data)
