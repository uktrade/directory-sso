import factory.fuzzy

from sso.user.tests.factories import UserFactory
from sso.verification.models import VerificationCode


class VerificationCodeFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = VerificationCode
