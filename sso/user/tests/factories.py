from datetime import datetime

import factory
import factory.fuzzy
from django.utils.timezone import make_aware

from sso.user import models


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: '%d@example.com' % n)
    last_login = factory.fuzzy.FuzzyDateTime(make_aware(datetime(2016, 11, 16)))

    class Meta:
        model = models.User


class UserProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    first_name = factory.fuzzy.FuzzyText()
    last_name = factory.fuzzy.FuzzyText()
    job_title = factory.fuzzy.FuzzyText()

    class Meta:
        model = models.UserProfile


class DataRetentionStatisticsFactory(factory.django.DjangoModelFactory):
    sso_user = factory.fuzzy.FuzzyInteger(low=1)
    company_user = factory.fuzzy.FuzzyInteger(low=1)
    company = factory.fuzzy.FuzzyInteger(low=1)

    class Meta:
        model = models.DataRetentionStatistics


class ServiceFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()

    class Meta:
        model = models.Service


class QuestionFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    name = factory.fuzzy.FuzzyText()

    class Meta:
        model = models.Question
