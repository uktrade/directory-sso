import logging

from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.decorators import decorator_from_middleware
from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import ListAPIView
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from sso.user import serializers
from sso.user.models import User, UserAnswer

logger = logging.getLogger(__name__)

NO_CREDENTIALS_MESSAGE = 'Authentication credentials were not provided.'
INCORRECT_CREDENTIALS_MESSAGE = 'Incorrect authentication credentials.'

ADDED_IPS_BY_DIRECTORY_SSO_PROXY_PAAS_ROUTER = 2
ADDED_IPS_BY_DIRECTORY_SSO_PROXY = 1
ADDED_IPS_BY_DIRECTORY_SSO_PAAS_ROUTER = 2
ADDED_IPS = (
    ADDED_IPS_BY_DIRECTORY_SSO_PROXY_PAAS_ROUTER
    + ADDED_IPS_BY_DIRECTORY_SSO_PROXY
    + ADDED_IPS_BY_DIRECTORY_SSO_PAAS_ROUTER
)


def _lookup_credentials(access_key_id):
    """Raises a HawkFail if the passed ID is not equal to
    settings.ACTIVITY_STREAM_ACCESS_KEY_ID
    """
    if not constant_time_compare(access_key_id, settings.ACTIVITY_STREAM_ACCESS_KEY_ID):
        raise HawkFail('No Hawk ID of {access_key_id}'.format(access_key_id=access_key_id))

    return {
        'id': settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
        'key': settings.ACTIVITY_STREAM_SECRET_ACCESS_KEY,
        'algorithm': 'sha256',
    }


def _authorise(request):
    """Raises a HawkFail if the passed request cannot be authenticated"""
    return Receiver(
        _lookup_credentials,
        request.META['HTTP_AUTHORIZATION'],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
    )


class _ActivityStreamAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        """This is returned as the WWW-Authenticate header when
        AuthenticationFailed is raised. DRF also requires this
        to send a 401 (as opposed to 403)
        """
        return 'Hawk'

    def authenticate(self, request):
        """Authenticates a request using two mechanisms:

        1. Ensure the request does not contain the X-Forwarded-For header
           (disallow access via public network)
        2. A Hawk signature in the Authorization header

        If either of these suggest we cannot authenticate, AuthenticationFailed
        is raised, as required in the DRF authentication flow
        """
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            logger.warning('Failed authentication: accessed from public network')
            raise AuthenticationFailed('Public network access denied')
        return self._authenticate_by_hawk(request)

    def _authenticate_by_hawk(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthenticationFailed(NO_CREDENTIALS_MESSAGE)

        try:
            hawk_receiver = _authorise(request)
        except HawkFail as e:
            logger.warning('Failed authentication {e}'.format(e=e))
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        return (None, hawk_receiver)


class _ActivityStreamHawkResponseMiddleware:
    """Adds the Server-Authorization header to the response, so the originator
    of the request can authenticate the response
    """

    def process_response(self, viewset, response):
        """Adds the Server-Authorization header to the response, so the originator
        of the request can authenticate the response
        """
        response['Server-Authorization'] = viewset.request.auth.respond(
            content=response.content, content_type=response['Content-Type']
        )
        return response


class ActivityStreamViewSet(ViewSet):
    """List-only view set for the activity stream"""

    authentication_classes = (_ActivityStreamAuthentication,)
    permission_classes = ()

    @decorator_from_middleware(_ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of activities"""
        return Response({'secret': 'content-for-pen-test'})


class ActivityStreamDirectorySSOUsersPagination(CursorPagination):
    ordering = ('modified', 'id')


class ActivityStreamDirectorySSOUsers(ListAPIView):
    authentication_classes = [_ActivityStreamAuthentication]
    permission_classes = []

    pagination_class = ActivityStreamDirectorySSOUsersPagination
    queryset = User.objects.all()
    serializer_class = serializers.ActivityStreamUsersSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset_page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset_page, many=True)

        page = {
            '@context': [
                'https://www.w3.org/ns/activitystreams',
            ],
            'type': 'Collection',
            'orderedItems': [
                {
                    'dit:application': 'DirectorySSO',
                    'id': f'dit:DirectorySSO:User:{user["id"]}:Update',
                    'published': user["modified"],
                    'type': 'Update',
                    'object': {
                        'id': f'dit:DirectorySSO:User:{user["id"]}',
                        'type': 'dit:DirectorySSO:User',
                        'dit:DirectorySSO:User:email': user['email'],
                        'dit:DirectorySSO:User:dateJoined': user['date_joined'],
                    },
                }
                for user in serializer.data
            ],
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
        }

        return Response(data=page)


class ActivityStreamDirectorySSOUserAnswersVFM(ListAPIView):
    authentication_classes = [_ActivityStreamAuthentication]
    permission_classes = []

    pagination_class = ActivityStreamDirectorySSOUsersPagination
    queryset = UserAnswer.objects.all()
    serializer_class = serializers.ActivityStreamUserAnswerSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset_page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset_page, many=True)
        page = {
            '@context': [
                'https://www.w3.org/ns/activitystreams',
            ],
            'type': 'Collection',
            'orderedItems': [
                {
                    'dit:application': 'DirectorySSO',
                    'id': f'dit:DirectorySSO:UserAnswer:{user_answer["id"]}:Update',
                    'published': user_answer["modified"],
                    'type': 'Update',
                    'object': {
                        'id': f'dit:DirectorySSO:UserAnswer:{user_answer["id"]}',
                        'type': 'dit:DirectorySSO:UserAnswer',
                        'dit:DirectorySSO:UserAnswer:user:id': user_answer["user_id"],
                        'dit:DirectorySSO:UserAnswer:answer': user_answer["answer"],
                        'dit:DirectorySSO:UserAnswer:question:id': user_answer["question_id"],
                        'dit:DirectorySSO:UserAnswer:question:title': user_answer["question_title"],
                        'dit:DirectorySSO:UserAnswer:answer_label': user_answer["answer_label"],
                    },
                }
                for user_answer in serializer.data
            ],
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
        }
        return Response(data=page)
