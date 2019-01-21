from datetime import datetime, timedelta

import pytest
from django.conf import settings

from sso.verification.models import VerificationCode

expiry_days = settings.VERIFICATION_EXPIRY_DAYS


@pytest.fixture
def verification_code():
    return VerificationCode(
    )


@pytest.mark.django_db
def test_verification_expired(verification_code):
    verification_code.created = datetime.now() - timedelta(days=expiry_days+1)

    assert verification_code.is_expired is True


@pytest.mark.django_db
def test_verification_not_expired(verification_code):
    verification_code.created = datetime.now() - timedelta(days=expiry_days-1)
    assert verification_code.is_expired is False
