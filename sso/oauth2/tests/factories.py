from datetime import datetime, timedelta

import factory
from oauth2_provider.models import AccessToken, Application

from sso.user.tests.factories import UserFactory


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application
    user = factory.SubFactory(UserFactory)


class AccessTokenFactory(factory.django.DjangoModelFactory):

    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    expires = datetime.now() + timedelta(minutes=60)
    token = factory.fuzzy.FuzzyText()

    class Meta:
        model = AccessToken
