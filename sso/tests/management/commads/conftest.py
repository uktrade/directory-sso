from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user():
    User = get_user_model()  # noqa
    user = User.objects.create(email='abc@xyz.com')
    yield user
    user.delete()


@pytest.fixture
def thirty_day_notification_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def@xyz.com')

    # user last_login on 3 years and 30 days ago
    today = datetime.now()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=30)
    # user created 5 years ago
    user.created = datetime.now() - timedelta(days=5 * 365)
    user.save()
    yield user
    user.delete()


@pytest.fixture
def fourteen_day_notification_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def1@xyz.com')

    # user last_login on 3 years and 14 days ago
    today = datetime.now()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=14)
    # user created 5 years ago
    user.created = datetime.now() - timedelta(days=5 * 365)
    user.save()
    yield user
    user.delete()


@pytest.fixture
def seven_day_notification_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def2@xyz.com')

    # user last_login on 3 years and 7 days ago
    today = datetime.utcnow()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=7)
    # user created 5 years ago
    user.created = today - timedelta(days=5 * 365)
    user.save()
    yield user
    user.delete()


@pytest.fixture
def zero_day_notification_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def3@xyz.com')

    # user last_login on 3 years ago
    today = datetime.utcnow()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=0)
    # user created 5 years ago
    user.created = today - timedelta(days=5 * 365)
    user.save()
    yield user
    user.delete()
