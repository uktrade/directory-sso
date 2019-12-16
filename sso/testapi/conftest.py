from datetime import datetime

import pytest
from allauth.account.models import EmailAddress
from django.utils.timezone import make_aware
from factory import Sequence, django, fuzzy

from sso.user import models
from sso.user.models import User


@pytest.fixture
def active_user():
    user = User.objects.create_user(
        email='dev@example.com',
        password='password',
        is_active=True,
        id=11
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
        id=1,
        user_id=user.id
    )
    return user


@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        email='inactive@user.com',
        password='password',
        is_active=False,
        id=22
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
        id=2,
        user_id=user.id
    )
    return user


class AutomatedTestUserFactory(django.DjangoModelFactory):
    email = Sequence(lambda n: f'test+{n}@directory.uktrade.io')
    last_login = fuzzy.FuzzyDateTime(
        make_aware(datetime(2016, 11, 16)))

    class Meta:
        model = models.User
