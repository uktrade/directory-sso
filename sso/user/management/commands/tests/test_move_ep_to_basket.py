import pytest
from django.core import management
from pathlib import Path

from sso.user.tests import factories
from sso.user import models
from sso.user.management.commands.move_ep_to_basket import read_csv_and_save_basket, inject_data


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


@pytest.fixture
def user_data_for_duplication_true(user_factory):
    user = models.User.objects.get(pk=3)
    data_market = models.UserData.objects.create(
        user=user, name="UserMarkets", data=[{'country_name': 'Iceland', 'country_iso2_code': 'IS'}]
    )
    data_product = models.UserData.objects.create(
        user=user, name="UserProducts", data=[{'commodity_code': '220300', 'commodity_name': 'Alcoholic beer'}]
    )

    return [data_market, data_product]


@pytest.fixture
def user_data_for_duplication_false(user_factory):
    user = models.User.objects.get(pk=4)

    data_market = models.UserData.objects.create(
        user=user,
        name="UserMarkets",
        data=[
            {'region': 'North America', 'country_name': 'United States', 'country_iso2_code': 'US'},
            {'country_name': 'Jamaica', 'country_iso2_code': None},
        ],
    )
    data_product = models.UserData.objects.create(
        user=user, name="UserProducts", data=[{'commodity_code': '440711', 'commodity_name': 'Wood'}]
    )

    return [data_market, data_product]


@pytest.fixture
def user_data_multi_data(user_factory):
    user = models.User.objects.get(pk=14)
    data_market = models.UserData.objects.create(
        user=user,
        name="UserMarkets",
        data=[
            {'region': 'North America', 'country_name': 'United States', 'country_iso2_code': 'US'},
            {'country_name': 'Afghanistan', 'country_iso2_code': 'AF'},
        ],
    )

    return data_market


@pytest.mark.django_db
def test_move_ep_to_basket(
    user_factory, user_data_factory, user_data_for_duplication_true, user_data_for_duplication_false
):
    management.call_command('move_ep_to_basket', 'sso/user/tests/ep_plan_factory.csv')


@pytest.mark.django_db
def test_move_ep_to_basket_no_file(user_factory, user_data_factory):
    with pytest.raises(Exception):
        management.call_command('move_ep_to_basket', 'no_file.csv')


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


@pytest.mark.django_db
def test_inject_data(user_data_multi_data):
    user = models.User.objects.get(pk=14)
    data_object = models.UserData.objects.filter(user=user, name="UserMarkets").first()

    test_list_countries = [
        {'region': 'North America', 'country_name': 'United States', 'country_iso2_code': 'US'},
        {'country_name': 'Afghanistan', 'country_iso2_code': 'AF'},
        {'country_name': 'Italy', 'country_iso2_code': None},
    ]
    test_list_no_dupe = [
        {'country_name': 'Italy', 'country_iso2_code': None},
        {'country_name': 'Jamaica', 'country_iso2_code': None},
    ]

    inject_data(user, "UserMarkets", test_list_no_dupe)
    data_object.refresh_from_db()
    assert data_object.data == [
        {'region': 'North America', 'country_name': 'United States', 'country_iso2_code': 'US'},
        {'country_name': 'Afghanistan', 'country_iso2_code': 'AF'},
        {'country_name': 'Italy', 'country_iso2_code': None},
        {'country_name': 'Jamaica', 'country_iso2_code': None},
    ]
