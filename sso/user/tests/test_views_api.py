import pytest
from unittest import mock

from django.urls import reverse
from rest_framework.test import APIClient

from sso.user.tests import factories
from sso.user import models
from sso.verification.models import VerificationCode


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_profile_data():
    return {
        'first_name': 'john',
        'last_name': 'smith',
        'mobile_phone_number': '0203044213',
        'job_title': 'Director',
    }


@pytest.fixture
def page_view_data():
    return {
        'page1': {
            'service': 'service-name',
            'page': 'page/url'
        },
        'page2': {
            'service': 'service-name',
            'page': 'page2/url'
        },
        'service_only': {
            'service': 'service-name'
        }
    }


@pytest.mark.django_db
def test_create_user_api_valid(api_client):
    new_email = 'test@test123.com'
    password = 'Abh129Jk392Hj2'

    response = api_client.post(
        reverse('api:user'),
        {'email': new_email, 'password': password},
        format='json'
    )
    assert response.status_code == 201
    assert response.json() == {
        'email': new_email,
        'verification_code': mock.ANY
    }

    assert models.User.objects.filter(email=new_email).count() == 1


@pytest.mark.django_db
def test_create_user_api_invalid_password(api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    response = api_client.post(
        reverse('api:user'),
        {'email': new_email, 'password': password},
        format='json'
    )
    assert response.status_code == 400

    assert models.User.objects.filter(email=new_email).count() == 0


@pytest.mark.django_db
@mock.patch('sso.user.models.User.objects.create_user')
def test_create_user_api_exception_rollback(mock_create, api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        response = api_client.post(
            reverse('api:user'),
            {'email': new_email, 'password': password},
            format='json'
        )
        assert response.status_code == 500
    assert models.User.objects.count() == 0
    assert VerificationCode.objects.count() == 0


@pytest.mark.django_db
@mock.patch('sso.verification.models.VerificationCode.objects.create')
def test_create_user_api_verification_exception_rollback(
        mock_create, api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        response = api_client.post(
            reverse('api:user'),
            {'email': new_email, 'password': password},
            format='json'
        )
        assert response.status_code == 500
    assert models.User.objects.count() == 0
    assert VerificationCode.objects.count() == 0


@pytest.mark.django_db
def test_create_user_profile(api_client):
    user = factories.UserFactory()
    data = {
        'first_name': 'john',
        'last_name': 'smith',
        'mobile_phone_number': '0203044213',
        'job_title': 'Director',
    }

    assert models.UserProfile.objects.filter(user=user).count() == 0
    api_client.force_authenticate(user=user)
    response = api_client.post(
        reverse('api:user-create-profile'),
        data,
        format='json'
    )

    instance = models.UserProfile.objects.last()
    assert response.status_code == 201
    assert instance.first_name == data['first_name']
    assert instance.last_name == data['last_name']
    assert instance.job_title == data['job_title']
    assert instance.mobile_phone_number == data['mobile_phone_number']


@pytest.mark.django_db
def test_create_user_profile_already_exists(api_client):
    profile = factories.UserProfileFactory()
    data = {
        'first_name': 'john',
        'last_name': 'smith',
        'mobile_phone_number': '0203044213',
        'job_title': 'Director',
    }

    api_client.force_authenticate(user=profile.user)
    response = api_client.post(
        reverse('api:user-create-profile'),
        data,
        format='json'
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_user_profile_no_auth(api_client):
    response = api_client.post(
        reverse('api:user-create-profile'),
        {},
        format='json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_update_user_profile(api_client, user_profile_data):

    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    response = api_client.patch(
        reverse('api:user-update-profile'),
        user_profile_data,
        format='json'
    )
    profile.refresh_from_db()
    assert response.status_code == 200
    assert profile.first_name == user_profile_data['first_name']
    assert profile.last_name == user_profile_data['last_name']
    assert profile.job_title == user_profile_data['job_title']
    assert profile.mobile_phone_number == user_profile_data['mobile_phone_number']


@pytest.mark.django_db
def test_update_user_profile_no_auth(api_client, user_profile_data):

    response = api_client.patch(
        reverse('api:user-update-profile'),
        user_profile_data,
        format='json'
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_set_page_view(api_client, page_view_data):

    def set_view(data):
        set_response = api_client.post(
            reverse('api:user-page-views'),
            data,
            format='json'
        )
        assert set_response.status_code == 200
        page_view = set_response.json().get('page_view')
        assert page_view['page'] == data['page']
        assert page_view['service'] == data['service']
        return page_view

    def get_view(data):
        response = api_client.get(
            reverse('api:user-page-views'),
            data,
            format='json'
        )
        assert response.status_code == 200
        return response.json().get('page_views')

    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    # Page not viewed
    page_views = get_view(page_view_data['page1'])
    assert page_views is None

    # Set a different to viewed - check our first page is not affected
    set_view(page_view_data['page2'])
    assert get_view(page_view_data['page1']) is None

    # Set first page to viewed and check
    set_view(page_view_data['page1'])
    page_views = get_view(page_view_data['page1'])
    assert len(page_views) == 1
    page_view = page_views[page_view_data['page1']['page']]
    assert page_view.get('service') == page_view_data['page1']['service']

    # get all page_views for service
    page_views = get_view(page_view_data['service_only'])
    assert len(page_views) == 2
    assert page_views[page_view_data['page1']['page']] is not None
    assert page_views[page_view_data['page2']['page']] is not None
