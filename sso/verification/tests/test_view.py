from datetime import date, datetime, timedelta

import dateutil.parser
import pytest
from allauth.account.models import EmailAddress
from django.core.cache import cache
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from freezegun import freeze_time
from pytz import UTC
from rest_framework.test import APIClient

from sso.user.tests.factories import UserFactory
from sso.verification import helpers, models
from sso.verification.tests.factories import VerificationCodeFactory


@pytest.fixture
def api_client():
    return APIClient()


@freeze_time("2018-01-14 12:00:01")
@pytest.mark.django_db
def test_regenerate_code(api_client):
    verification_code = VerificationCodeFactory()
    old_code = verification_code.code

    response = api_client.post(
        reverse('api:verification-code-regenerate'),
        {
            'email': verification_code.user.email,
        },
        format='json',
    )
    assert response.status_code == 200
    verification_code.refresh_from_db()
    assert verification_code.created == datetime(2018, 1, 14, 12, 0, 1, tzinfo=UTC)
    assert verification_code.code != old_code
    new_code = response.json()
    assert new_code['code'] == verification_code.code
    expiration_date = dateutil.parser.parse(new_code['expiration_date'])
    assert expiration_date == verification_code.expiration_date


@pytest.mark.django_db
def test_regenerate_code_verified_code(api_client):
    verification_code = VerificationCodeFactory()
    original_code = verification_code.code
    original_date_verified = date(2018, 1, 14)
    verification_code.date_verified = original_date_verified
    verification_code.save()

    response = api_client.post(
        reverse('api:verification-code-regenerate'),
        {
            'email': verification_code.user.email,
        },
        format='json',
    )
    assert response.status_code == 400
    verification_code.refresh_from_db()
    assert verification_code.date_verified == original_date_verified
    assert verification_code.code == original_code


@pytest.mark.django_db
def test_regenerate_code_no_user(api_client):

    assert models.VerificationCode.objects.count() == 0

    response = api_client.post(
        reverse('api:verification-code-regenerate'),
        {
            'email': 'donot@exist.com',
        },
        format='json',
    )

    assert response.status_code == 404
    assert models.VerificationCode.objects.count() == 0


@freeze_time("2018-01-14 12:00:01")
@pytest.mark.django_db
def test_verify_verification_code(api_client):
    verification_code = VerificationCodeFactory()

    assert verification_code.code

    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': verification_code.code,
            'email': verification_code.user.email,
        },
        format='json',
    )

    verification_code.refresh_from_db()

    assert response.status_code == 200
    assert response.cookies['debug_sso_session_cookie']
    assert response.cookies['sso_display_logged_in'].value == 'true'
    assert verification_code.date_verified == date(2018, 1, 14)

    assert (
        EmailAddress.objects.filter(
            user=verification_code.user,
            verified=True,
            email=verification_code.user.email,
            primary=True,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_verify_verification_code_invalid(api_client):
    verification_code = VerificationCodeFactory()

    assert verification_code.code

    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': '12345',
            'email': verification_code.user.email,
        },
        format='json',
    )

    assert response.status_code == 400
    assert verification_code.date_verified is None


@pytest.mark.django_db
def test_verify_verification_code_expired(api_client):
    with freeze_time(now() - timedelta(days=100)):
        verification_code = VerificationCodeFactory()

    url = reverse('api:verification-code-verify')
    response = api_client.post(url, {'code': '12345', 'email': verification_code.user.email}, format='json')

    assert response.status_code == 400
    assert verification_code.date_verified is None


@pytest.mark.django_db
def test_verify_no_verification_code(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)

    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': 'my-name-is-jeff',
            'email': user.email,
        },
        format='json',
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_verify_verification_code_limit_exceeded(api_client):
    cache.clear()

    verification_code = VerificationCodeFactory()

    url = reverse('api:verification-code-verify')
    invalid_code = '1234'

    assert verification_code.code

    for i in range(13):
        response = api_client.post(
            url,
            {
                'code': invalid_code,
                'email': verification_code.user.email,
            },
            format='json',
        )
        if i < 12:
            assert response.status_code == 400
        else:
            assert response.status_code == 403


@pytest.mark.django_db
def test_verify_verification_code_with_uidb64_and_token(api_client):
    cache.clear()

    verification_code = VerificationCodeFactory()
    uidb64 = urlsafe_base64_encode(force_bytes(verification_code.user.pk))
    token = helpers.verification_token.make_token(verification_code.user)
    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': verification_code.code,
            'uidb64': uidb64,
            'token': token,
        },
        format='json',
    )
    assert response.json()['email'] == verification_code.user.email
    assert response.status_code == 200


@pytest.mark.django_db
def test_verify_verification_code_with_token_missing(api_client):
    cache.clear()

    verification_code = VerificationCodeFactory()
    uidb64 = urlsafe_base64_encode(force_bytes(verification_code.user.pk))
    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': verification_code.code,
            'uidb64': uidb64,
        },
        format='json',
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_verify_verification_code_with_wrong_uidb64(api_client):
    cache.clear()

    verification_code = VerificationCodeFactory()
    uidb64 = 'aBcDe'
    token = helpers.verification_token.make_token(verification_code.user)
    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': verification_code.code,
            'uidb64': uidb64,
            'token': token,
        },
        format='json',
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_verify_verification_code_with_wrong_token(api_client):
    cache.clear()

    verification_code = VerificationCodeFactory()
    uidb64 = urlsafe_base64_encode(force_bytes(verification_code.user.pk))
    token = '12345'
    url = reverse('api:verification-code-verify')
    response = api_client.post(
        url,
        {
            'code': verification_code.code,
            'uidb64': uidb64,
            'token': token,
        },
        format='json',
    )

    assert response.status_code == 404
