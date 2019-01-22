from datetime import timedelta, date
from django.utils.timezone import now

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
from freezegun import freeze_time


from sso.user.tests.factories import UserFactory
from sso.verification.tests.factories import VerificationFactory
from sso.verification import models


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verification_code():
    return VerificationFactory()


@pytest.mark.django_db
def test_create_verification_code_no_auth(api_client):
    response = api_client.post(
        reverse('api:verification-code-verify'),
        {},
        format='json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_verification_code(api_client):
    user = UserFactory()

    assert models.VerificationCode.objects.filter(user=user).count() == 0

    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api:verification-code-verify'),
        {},
        format='json'
    )

    assert response.status_code == 201
    assert models.VerificationCode.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_verify_verification_code(api_client, verification_code):
    freezer = freeze_time("2018-01-14 12:00:01")
    freezer.start()

    user = verification_code.user
    api_client.force_authenticate(user=user)

    verification_code.refresh_from_db()
    assert verification_code.code

    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url, {'code': verification_code.code}, format='json'
    )

    assert response.status_code == 200

    verification_code.refresh_from_db()
    freezer.stop()
    assert verification_code.date_verified == date(2018, 1, 14)


@pytest.mark.django_db
def test_verify_verification_code_invalid(api_client, verification_code):
    user = verification_code.user
    api_client.force_authenticate(user=user)
    verification_code.refresh_from_db()
    assert verification_code.code

    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url, {'code': '12345'}, format='json'
    )

    assert response.status_code == 400

    verification_code.refresh_from_db()

    assert verification_code.date_verified is None


@pytest.mark.django_db
def test_verify_verification_code_expired(api_client, verification_code):
    verification_code.created = now() - timedelta(days=100)
    verification_code.save()
    user = verification_code.user
    api_client.force_authenticate(user=user)
    verification_code.refresh_from_db()

    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url, {'code': '12345'}, format='json'
    )

    assert response.status_code == 400

    verification_code.refresh_from_db()

    assert verification_code.date_verified is None
