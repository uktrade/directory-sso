from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from conf.signature import SignatureCheckPermission
from core.authentication import SessionAuthentication
from sso.user import serializers
from sso.user.models import LessonCompleted, Service, User, UserData, UserProfile
from sso.user.utils import (
    get_lesson_completed,
    get_page_view,
    get_questionnaire,
    set_lesson_completed,
    set_page_view,
    set_questionnaire_answer,
)


class UserCreateAPIView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer
    permission_classes = [SignatureCheckPermission]

    def create(self, request, *args, **kwargs):
        try:
            User.objects.get(email__iexact=request.data.get('email'))
        except ObjectDoesNotExist:
            response = super().create(request, *args, **kwargs)
            phone_number = request.data.get('mobile_phone_number')
            if response.status_code == 201 and phone_number:
                user = User.objects.get(email__iexact=request.data.get('email'))
                UserProfile.objects.create(user=user, mobile_phone_number=phone_number)
            return response

        return Response(status=status.HTTP_409_CONFLICT)


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


class LessonCompletedAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def post(self, request, query=None, *args, **kwargs):
        service = request.data.get('service')
        lesson_page = request.data.get('lesson_page')
        lesson = request.data.get('lesson')
        module = request.data.get('module')
        lesson_completed = set_lesson_completed(self.request.user, service, lesson_page, lesson, module)
        return Response(status=200, data={'result': 'ok', 'lesson_completed': lesson_completed.to_dict()})

    def get(self, request):
        service = request.query_params.get('service')
        filter_dict = dict()
        for item in request.query_params:
            if item not in ('user', 'service'):
                filter_dict[item] = request.query_params.get(item)

        lesson_completed = get_lesson_completed(self.request.user, service, **filter_dict)
        data = {'result': 'ok'}
        if lesson_completed and lesson_completed.count():
            lesson_completed_lst = []
            for lesson in lesson_completed:
                lesson_completed_lst.append(lesson.to_dict())
            data['lesson_completed'] = lesson_completed_lst
        return Response(status=200, data=data)

    def delete(self, request, format=None):
        service = Service.objects.get(name=request.data.get('service'))
        lesson_id = request.data.get('lesson')
        try:
            lesson = LessonCompleted.objects.get(service=service, lesson=lesson_id, user=request.user)
        except ObjectDoesNotExist:
            lesson = None

        if not lesson or lesson.user_id != request.user.id:
            return Response(status=status.HTTP_502_BAD_GATEWAY)
        response = lesson.delete()
        return Response(response)


class UserQuestionnaireView(GenericAPIView):
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        service = request.query_params.get('service')
        data = {'result': 'ok'}
        data.update(get_questionnaire(self.request.user, service) or {})
        return Response(status=200, data=data)

    def post(self, request, *args, **kwargs):
        service = request.data.get('service')
        question_id = request.data.get('question_id')
        user_answer = request.data.get('answer')
        set_questionnaire_answer(self.request.user, service, question_id, user_answer)
        data = {'result': 'ok'}
        data.update(get_questionnaire(self.request.user, service) or {})
        return Response(status=200, data=data)


class UserDataView(GenericAPIView):
    permission_classes = [IsAuthenticated, SignatureCheckPermission]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        names = request.query_params.getlist('name', '')
        data = {}
        for name in names:
            try:
                data[name] = UserData.objects.get(user=self.request.user, name=name).data
            except ObjectDoesNotExist:
                pass
        return Response(status=200, data=data)

    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        name = request.data.get('name')
        try:
            data_object = UserData.objects.get(user=self.request.user, name=name)
        except ObjectDoesNotExist:
            data_object = UserData(user=self.request.user, name=name)

        data_object.data = data
        data_object.save()
        return Response(status=200, data={'result': 'ok'})


@method_decorator(csrf_exempt, name='get')
class CSRFView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return Response(status=200, data={'csrftoken': token})
