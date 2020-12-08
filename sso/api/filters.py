import django_filters
from django.conf import settings

from sso.user import models


class LastLoginFilter(django_filters.rest_framework.FilterSet):
    error_messages = {'invalid': 'Invalid date format. Expected {0}'.format(', '.join(settings.DATETIME_INPUT_FORMATS))}

    start = django_filters.DateTimeFilter(
        field_name='last_login',
        lookup_expr='gte',
        error_messages=error_messages,
        input_formats=settings.DATETIME_INPUT_FORMATS,
    )
    end = django_filters.DateTimeFilter(
        field_name='last_login',
        lookup_expr='lte',
        error_messages=error_messages,
        input_formats=settings.DATETIME_INPUT_FORMATS,
    )

    class Meta:
        model = models.User
        fields = ['end', 'start']
