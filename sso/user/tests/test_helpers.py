import pytest
from pathlib import Path

from sso.user.tests import factories
from sso.user import models
from sso.user.helpers import read_csv_and_save_basket


@pytest.fixture
def user_factory():
    users = []
    for num in range(1, 15):
        user = factories.UserFactory.create(pk=num)
        users.append(user)

    return users


@pytest.fixture
def user_data_factory(user_factory):
    user = models.User.objects.get(pk=1)
    data = models.UserData.objects.create(user=user, name="UserMarkets")

    return data


@pytest.mark.django_db
def test_read_csv_and_save_basket(user_factory, user_data_factory):
    expected_product = [{'commodity_code': '080810', 'commodity_name': 'apple'}]
    expected_market = [{'country_name': 'Italy', 'country_iso2_code': None}]
    my_file = Path("sso/user/tests/ep_plan_factory.csv")
    market = None
    product = None
    read_csv_and_save_basket(my_file)

    user_exist = models.User.objects.get(pk=1)
    data = models.UserData.objects.filter(user=user_exist)
    data_len = len(models.UserData.objects.all())

    for value in data:
        if value.name == "UserMarkets":
            market = value.data
        if value.name == "UserProducts":
            product = value.data

    assert expected_product == product
    assert expected_market == market
    assert data_len == 16
