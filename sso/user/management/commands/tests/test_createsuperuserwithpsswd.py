from unittest.mock import patch

import pytest

from django.core.management import call_command

from sso.user.models import User


@pytest.mark.django_db
def test_createsuperuserwithpsswd():
    call_command(
        "createsuperuserwithpsswd",
        "--email=test@example.com",
        "--password=test",
    )

    user = User.objects.last()
    assert user.email == "test@example.com"
    assert user.check_password('test') is True


@pytest.mark.django_db
@patch.object(User, 'REQUIRED_FIELDS', ['utm'])
def test_test_createsuperuserwithpsswd_required_fields():
    call_command(
        "createsuperuserwithpsswd",
        "--email=test@example.com",
        "--password=test",
        "--utm=things",
    )

    user = User.objects.last()
    assert user.email == "test@example.com"
    assert user.check_password('test') is True
    assert user.utm == "things"
