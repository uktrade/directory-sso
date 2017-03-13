import django_filters

from sso.user import models


class LastLoginFilter(django_filters.rest_framework.FilterSet):
    start = django_filters.DateFilter(name='last_login', lookup_expr='gte')
    end = django_filters.DateFilter(name='last_login', lookup_expr='lte')

    class Meta:
        model = models.User
        fields = ['end', 'start']
