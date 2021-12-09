from datetime import timedelta
import factory
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

from sso.user.tests.factories import UserFactory
from sso.user.models import User
from oauth2_provider.models import AccessToken, Application


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


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: '%d@example.com' % n)
    password = 'pass'
    is_superuser = True


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    client_id = 'test'
    user = factory.SubFactory(UserFactory)
    client_type = 'Confidential'
    authorization_grant_type = 'Authorization code'
    skip_authorization = True


class AccessTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccessToken

    user = factory.SubFactory(UserFactory)
    token = 'test'
    application = factory.SubFactory(ApplicationFactory)
    expires = timezone.now() + timedelta(days=1)
    scope = 'profile'
