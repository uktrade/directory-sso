import pytest
from pathlib import Path

from sso.user.tests import factories
from sso.user import models
from sso.user.helpers import read_csv_and_save_basket


@pytest.fixture
def user_factory():
    users = []
    for num in range(1, 10):
        user = factories.UserFactory.create(pk=num)
        users.append(user)

    return users


@pytest.mark.django_db
def test_read_csv_and_save_basket(user_factory):
    expected_country = [{'country_name': 'Italy', 'country_iso2_code': None}]
    expected_market = [{'commodity_code': '080810', 'commodity_name': 'apple'}]

    my_file = Path("sso/user/tests/ep_plan_factory.csv")
    read_csv_and_save_basket(my_file)

    user_exist = models.User.objects.get(pk=1)
    data = models.UserData.objects.filter(user=user_exist)
    country = data[0].data
    market = data[1].data
    data_len = len(models.UserData.objects.all())

    assert country == expected_country
    assert market == expected_market
    assert data_len == 18
