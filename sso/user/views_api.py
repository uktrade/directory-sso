from rest_framework.generics import CreateAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import IntegrityError

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.user import serializers
from sso.user.utils import get_page_view, set_page_view


class UserCreateAPIView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer
    permission_classes = [SignatureCheckPermission]


class UserProfileCreateAPIView(CreateAPIView):
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
        except IntegrityError as error:
            if 'already exists' in str(error):
                return Response(status=200)
            else:
                raise
        else:
            return Response(status=201)


class UserProfileUpdateAPIView(UpdateAPIView):
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]
    lookup_field = 'user_id'

    def get_object(self):
        return self.request.user.user_profile


class UserPageViewAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def post(self, request, query=None, *args, **kwargs):
        service = request.data.get('service')
        page = request.data.get('page')
        page_view = set_page_view(self.request.user, service, page)
        return Response(status=200, data={'result': 'ok', 'page_view': page_view.to_dict()})

    def get(self, request):
        service = request.query_params.get('service')
        page = request.query_params.get('page')
        page_views = get_page_view(self.request.user, service, page)
        data = {'result': 'ok'}
        if page_views and page_views.count():
            page_views_dict = {}
            for page_view in page_views:
                page_views_dict[page_view.service_page.page_name] = page_view.to_dict()
            data['page_views'] = page_views_dict
        return Response(status=200, data=data)
