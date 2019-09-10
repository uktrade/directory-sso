from datetime import timedelta

import factory
from oauth2_provider.models import AccessToken, Application

from django.utils import timezone

from sso.user.tests.factories import UserFactory


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application
    user = factory.SubFactory(UserFactory)


class AccessTokenFactory(factory.django.DjangoModelFactory):

    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    expires = timezone.now() + timedelta(minutes=60)
    token = factory.fuzzy.FuzzyText()

    class Meta:
        model = AccessToken


def build_historic_access_token_factory(apps):

    class HistoricUserFactory(UserFactory):
        class Meta:
            model = apps.get_model('user', 'User')

    class HistoricApplicationFactory(ApplicationFactory):
        class Meta:
            model = apps.get_model('oauth2_provider', 'Application')
        user = factory.SubFactory(HistoricUserFactory)

    class HistoricAccessTokenFactory(AccessTokenFactory):
        class Meta:
            model = apps.get_model('oauth2_provider', 'AccessToken')
        user = factory.SubFactory(HistoricUserFactory)
        application = factory.SubFactory(HistoricApplicationFactory)

    return HistoricAccessTokenFactory
