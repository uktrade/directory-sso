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
    user = User.objects.create(email='def_30@xyz.com')

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
    user = User.objects.create(email='def_14@xyz.com')

    # user last_login on 3 years and 14 days ago
    today = datetime.now()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=14)
    # user created 5 years ago
    user.created = datetime.now() - timedelta(days=5 * 365)
    user.inactivity_notification = 1
    user.save()
    yield user
    user.delete()


@pytest.fixture
def seven_day_notification_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def_7@xyz.com')

    # user last_login on 3 years and 7 days ago
    today = datetime.now()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=7)
    # user created 5 years ago
    user.created = today - timedelta(days=5 * 365)
    user.inactivity_notification = 2
    user.save()
    yield user
    user.delete()


@pytest.fixture
def zero_day_notification_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def_0@xyz.com')

    # user last_login on 3 years ago
    today = datetime.now()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=0)
    # user created 5 years ago
    user.created = today - timedelta(days=5 * 365)
    user.inactivity_notification = 3
    user.save()
    yield user
    user.delete()


@pytest.fixture
def inactive_user():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def_as@xyz.com')

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
def inactive_user_2():
    """Fixture for old user who's last login and created three years ago"""
    User = get_user_model()  # noqa
    user = User.objects.create(email='def_user_2@xyz.com')

    # user last_login on 3 years and 30 days ago
    today = datetime.now()
    three_year_old = today - timedelta(days=3 * 365)
    user.last_login = three_year_old - timedelta(days=30)
    # user created 5 years ago
    user.created = datetime.now() - timedelta(days=5 * 365)
    user.save()
    yield user
    user.delete()
