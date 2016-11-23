from django.core.management import call_command
from sso.user.models import User

import pytest


@pytest.mark.django_db
def test_createsuperuserwithpsswd():
    call_command(
        "createsuperuserwithpsswd",
        "--email=test@example.com",
        "--password=test"
    )

    last_user = User.objects.last()
    assert last_user.email == "test@example.com"
