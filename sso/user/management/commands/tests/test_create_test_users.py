import pytest

from django.core.management import call_command

from sso.user.models import User


@pytest.mark.django_db
def test_create_test_users():
    call_command("create_test_users")

    unverified_user = User.objects.last()
    assert unverified_user.email == "unverified@example.com"
    assert unverified_user.check_password('passwordpassword') is True

    verified_user = User.objects.first()
    assert verified_user.email == "verified@example.com"
    assert verified_user.check_password('passwordpassword') is True
