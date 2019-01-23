from freezegun import freeze_time
import pytest

from django.conf import settings
from datetime import timedelta
from django.utils.timezone import now

from sso.verification.tests import factories


@pytest.mark.django_db
def test_verification_expired():
    created = now() - timedelta(days=settings.VERIFICATION_EXPIRY_DAYS+1)
    with freeze_time(created):
        verification_code = factories.VerificationCodeFactory()

    assert verification_code.is_expired is True


@pytest.mark.django_db
def test_verification_not_expired():
    created = now() - timedelta(days=settings.VERIFICATION_EXPIRY_DAYS-1)
    with freeze_time(created):
        verification_code = factories.VerificationCodeFactory()

    assert verification_code.is_expired is False


@pytest.mark.django_db
def test_verification_model():
    verification_code = factories.VerificationCodeFactory()
    assert str(verification_code) == str(verification_code.user)
