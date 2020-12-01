import pytest
from allauth.account.models import EmailAddress
from django.core.management import call_command

from sso.user.models import User


@pytest.mark.django_db
def test_load_test_fixture():
    try:
        call_command('loaddata', 'test_fixtures/load_tests.json')
    except:  # noqa: E722
        raise AssertionError("Load test fixtures are broken")
    assert User.objects.all().count() == 25
    assert EmailAddress.objects.all().count() == 25
