from datetime import datetime, timedelta
import pytest

from sso.verification.models import Validation


@pytest.fixture
def validation():
    return Validation(
        is_verified=False,
    )


@pytest.mark.django_db
def test_validation_expired(validation):
    validation.created = datetime.now() - timedelta(
            days=validation.expiry_days+1
    )

    assert validation.is_expired is True


@pytest.mark.django_db
def test_verification_not_expired(validation):
    validation.created = datetime.now() - timedelta(
        days=validation.expiry_days-1
    )
    assert validation.is_expired is False
