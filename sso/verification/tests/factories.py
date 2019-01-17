import factory.fuzzy

from sso.verification.models import Validation
from sso.user.tests.factories import UserFactory


class ValidationFactory(factory.django.DjangoModelFactory):
    code = factory.fuzzy.FuzzyText(length=12)
    expiry_days = 3
    is_verified = False
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Validation
