import factory.fuzzy

from sso.user.tests.factories import UserFactory
from sso.verification.models import VerificationCode
import datetime


class VerificationCodeFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    date_verified = datetime.datetime(2021, 12, 29)

    class Meta:
        model = VerificationCode
