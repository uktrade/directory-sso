from datetime import datetime, timedelta
import pytest

from sso.verification.models import VerificationCode


@pytest.fixture
def verification_code():
    return VerificationCode(
        is_verified=False,
    )


@pytest.mark.django_db
def test_validation_expired(verification_code):
    verification_code.created = datetime.now() - timedelta(
            days=verification_code.expiry_days+1
    )

    assert verification_code.is_expired is True


@pytest.mark.django_db
def test_verification_not_expired(verification_code):
    verification_code.created = datetime.now() - timedelta(
        days=verification_code.expiry_days-1
    )
    assert verification_code.is_expired is False
