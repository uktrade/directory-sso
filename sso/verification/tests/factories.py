import factory.fuzzy

from sso.verification.models import VerificationCode
from sso.user.tests.factories import UserFactory


class VerificationCodeFactory(factory.django.DjangoModelFactory):
    code = factory.fuzzy.FuzzyText(length=5)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = VerificationCode
