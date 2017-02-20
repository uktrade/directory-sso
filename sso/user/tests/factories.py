from datetime import datetime

import factory
import factory.fuzzy

from django.utils.timezone import make_aware

from sso.user.models import User


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: '%d@example.com' % n)
    last_login = factory.fuzzy.FuzzyDateTime(
        make_aware(datetime(2016, 11, 16)))

    class Meta:
        model = User
