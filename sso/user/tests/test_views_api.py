import json
from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from sso.user import models
from sso.user.tests import factories
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
def user_partial_profile_data():
    return {
        'first_name': 'Magna',
        'last_name': 'User',
    }


@pytest.fixture
def page_view_data():
    return {
        'page1': {'service': 'service-name', 'page': 'page/url'},
        'page2': {'service': 'service-name', 'page': 'page2/url'},
        'service_only': {'service': 'service-name'},
    }


@pytest.mark.django_db
def test_create_user_api_valid(api_client):
    new_email = 'test@test123.com'
    password = 'Abh129Jk392Hj2'

    response = api_client.post(reverse('api:user'), {'email': new_email, 'password': password}, format='json')
    assert response.status_code == 201
    assert response.json() == {'email': new_email, 'verification_code': mock.ANY}

    assert models.User.objects.filter(email=new_email).count() == 1


@pytest.mark.django_db
def test_create_user_api_invalid_password(api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    response = api_client.post(reverse('api:user'), {'email': new_email, 'password': password}, format='json')
    assert response.status_code == 400

    assert models.User.objects.filter(email=new_email).count() == 0


@pytest.mark.django_db
@mock.patch('sso.user.models.User.objects.create_user')
def test_create_user_api_exception_rollback(mock_create, api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        response = api_client.post(reverse('api:user'), {'email': new_email, 'password': password}, format='json')
        assert response.status_code == 500
    assert models.User.objects.count() == 0
    assert VerificationCode.objects.count() == 0


@pytest.mark.django_db
@mock.patch('sso.verification.models.VerificationCode.objects.create')
def test_create_user_api_verification_exception_rollback(mock_create, api_client):
    new_email = 'test@test123.com'
    password = 'mypassword'

    mock_create.side_effect = Exception('!')

    with pytest.raises(Exception):
        response = api_client.post(reverse('api:user'), {'email': new_email, 'password': password}, format='json')
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
    response = api_client.post(reverse('api:user-create-profile'), data, format='json')

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
    response = api_client.post(reverse('api:user-create-profile'), data, format='json')

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_user_profile_no_auth(api_client):
    response = api_client.post(reverse('api:user-create-profile'), {}, format='json')
    assert response.status_code == 401


@pytest.mark.django_db
def test_update_user_profile(api_client, user_profile_data):

    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    response = api_client.patch(reverse('api:user-update-profile'), user_profile_data, format='json')
    profile.refresh_from_db()
    assert response.status_code == 200
    assert profile.first_name == user_profile_data['first_name']
    assert profile.last_name == user_profile_data['last_name']
    assert profile.job_title == user_profile_data['job_title']
    assert profile.mobile_phone_number == user_profile_data['mobile_phone_number']


@pytest.mark.django_db
def test_update_partial_user_profile(api_client, user_partial_profile_data):

    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    response = api_client.patch(reverse('api:user-update-profile'), user_partial_profile_data, format='json')
    profile.refresh_from_db()
    assert response.status_code == 200
    assert profile.first_name == user_partial_profile_data['first_name']
    assert profile.last_name == user_partial_profile_data['last_name']


@pytest.mark.django_db
def test_update_user_profile_no_auth(api_client, user_profile_data):

    response = api_client.patch(reverse('api:user-update-profile'), user_profile_data, format='json')

    assert response.status_code == 401


@pytest.mark.django_db
def test_set_page_view(api_client, page_view_data):
    def set_view(data):
        set_response = api_client.post(reverse('api:user-page-views'), data, format='json')
        assert set_response.status_code == 200
        page_view = set_response.json().get('page_view')
        assert page_view['page'] == data['page']
        assert page_view['service'] == data['service']
        return page_view

    def get_view(data):
        response = api_client.get(reverse('api:user-page-views'), data, format='json')
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


@pytest.fixture()
def set_lesson_completed(api_client):
    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    set_data = {'user': profile.user.pk, 'lesson_page': 'my-new-lesson', 'lesson': 99, 'module': 1, 'service': 'great'}
    return api_client.post(reverse('api:user-lesson-completed'), set_data, format='json')


@pytest.mark.django_db
def test_set_lesson_completed(set_lesson_completed):
    set_response = set_lesson_completed
    assert set_response.status_code == 200
    lesson_completed = set_response.json().get('lesson_completed')
    assert lesson_completed['lesson_page'] == lesson_completed['lesson_page']
    assert lesson_completed['service'] == lesson_completed['service']
    return lesson_completed


@pytest.mark.django_db
def test_get_lesson_completed(api_client, set_lesson_completed):

    set_response = set_lesson_completed
    assert set_response.status_code == 200
    lesson_completed = set_response.json().get('lesson_completed')

    data = {
        'service': 'great',
        'user': lesson_completed['user'],
        'lesson_page': 'my-new-lesson',
    }
    response = api_client.get(reverse('api:user-lesson-completed'), data, format='json')
    assert response.status_code == 200
    return response.json().get('lessson_completed')


@pytest.mark.django_db
def test_get_multiple_lesson_completed(api_client, set_lesson_completed):
    set_response = set_lesson_completed
    assert set_response.status_code == 200
    lesson_completed = set_response.json().get('lesson_completed')

    data = {
        'user': lesson_completed['user'],
        'lesson_page': 'my-new-lesson',
        'lesson': 9,
        'module': 1,
        'service': 'great',
    }
    set_response = api_client.post(reverse('api:user-lesson-completed'), data, format='json')
    assert set_response.status_code == 200

    data = {
        'service': 'great',
        'user': lesson_completed['user'],
        'module': '1',
    }
    response = api_client.get(reverse('api:user-lesson-completed'), data, format='json')
    assert response.status_code == 200
    return response.json().get('lessson_completed')


@pytest.mark.django_db
def test_get_not_existing_lesson(api_client):

    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    data = {
        'service': 'great',
        'user': profile.user.pk,
        'lesson_page': 'dummy-page',
    }
    response = api_client.get(reverse('api:user-lesson-completed'), data, format='json')

    assert response.status_code == 200
    assert response.json().get('lessson_completed') is None


@pytest.mark.django_db
def test_delete_endpoint_for_lesson_completed(api_client, set_lesson_completed):

    data = json.loads(set_lesson_completed.content)
    assert set_lesson_completed.status_code == 200

    data = {
        'service': 'great',
        'user_id': data['lesson_completed']['user'],
        'lesson': data['lesson_completed']['lesson'],
    }

    response = api_client.delete(
        reverse(
            'api:user-lesson-completed',
        ),
        data=data,
        format='json',
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_for_mutliple_lesson_completed(api_client, set_lesson_completed):
    """
    This test where multiple user completed same lesson and delete should delete user specific lesson
    """

    data = json.loads(set_lesson_completed.content)
    assert set_lesson_completed.status_code == 200

    profile = factories.UserProfileFactory()
    api_client.force_authenticate(user=profile.user)

    set_data = {'user': profile.user.pk, 'lesson_page': 'my-new-lesson', 'lesson': 99, 'module': 1, 'service': 'great'}
    api_client.post(reverse('api:user-lesson-completed'), set_data, format='json')
    data = {
        'service': 'great',
        'user_id': data['lesson_completed']['user'],
        'lesson': data['lesson_completed']['lesson'],
    }

    response = api_client.delete(
        reverse(
            'api:user-lesson-completed',
        ),
        data=data,
        format='json',
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_endpoint_no_existing_lesson_completed(api_client, set_lesson_completed):

    data = json.loads(set_lesson_completed.content)
    assert set_lesson_completed.status_code == 200

    data = {
        'service': 'great',
        'user_id': data['lesson_completed']['user'],
        'lesson': 9999,  # non existing lesson
    }
    response = api_client.delete(
        reverse(
            'api:user-lesson-completed',
        ),
        data=data,
        format='json',
    )
    assert response.status_code == 502


@pytest.mark.django_db
def test_delete_endpoint_for_lesson_completed_for_non_owner(api_client, set_lesson_completed):
    other_user = factories.UserProfileFactory()

    data = json.loads(set_lesson_completed.content)
    assert set_lesson_completed.status_code == 200

    data = {
        'service': 'great',
        'user_id': other_user.id,
        'lesson': data['lesson_completed']['lesson'],
    }

    response = api_client.delete(
        reverse(
            'api:user-lesson-completed',
        ),
        data=data,
        format='json',
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_user_questionnaire(api_client):
    user = factories.UserFactory()
    api_client.force_authenticate(user=user)

    data = {'service': 'great'}

    response = api_client.get(reverse('api:user-questionnaire'), data, format='json')

    assert response.status_code == 200


@pytest.mark.django_db
def test_set_user_questionnaire_answer(api_client):
    user = factories.UserFactory()
    api_client.force_authenticate(user=user)

    set_data = {'service': 'great', 'question_id': 99, 'answer': 'answer'}

    response = api_client.post(reverse('api:user-questionnaire'), set_data, format='json')

    assert response.status_code == 200


@pytest.mark.django_db
def test_set_user_questionnaire_answer_invalid(api_client):
    user = factories.UserFactory()
    api_client.force_authenticate(user=user)

    set_data = {'service': 'great', 'question_id': 99, 'answer': ''}

    response = api_client.post(reverse('api:user-questionnaire'), set_data, format='json')
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_and_set_user_data(api_client):
    user = factories.UserFactory()
    api_client.force_authenticate(user=user)
    url = reverse('api:user-data')

    # Call set twice to put two objects in db
    response = api_client.post(url, {'name': 'data-object1', 'data': {'test': 1}}, format='json')
    assert response.status_code == 200

    response = api_client.post(url, {'name': 'data-object2', 'data': {'test': 2}}, format='json')
    assert response.status_code == 200

    # Read them back
    assert api_client.get(url, {'name': 'data-object1'}, format='json').json().get('data-object1') == {'test': 1}
    assert api_client.get(url, {'name': 'data-object2'}, format='json').json().get('data-object2') == {'test': 2}

    # Update one and check the change
    response = api_client.post(url, {'name': 'data-object1', 'data': {'test': 'updated'}}, format='json')
    assert api_client.get(url, {'name': 'data-object1'}, format='json').json().get('data-object1') == {
        'test': 'updated'
    }
    assert api_client.get(url, {'name': 'data-object2'}, format='json').json().get('data-object2') == {'test': 2}

    # Read them back in one request
    both = api_client.get(url, {'name': ['data-object1', 'data-object2']}, format='json').json()
    assert both.get('data-object1') == {'test': 'updated'}
    assert both.get('data-object2') == {'test': 2}
