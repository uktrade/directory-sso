from unittest import mock

import pytest
from allauth.socialaccount.models import SocialAccount
from directory_constants import urls

from sso.user import utils
from sso.user.tests.factories import QuestionFactory, ServiceFactory, UserAnswerFactory, UserFactory


def test_get_social_account_image_google():
    account = SocialAccount(
        extra_data={
            'id': '123',
            'email': 'jim@example.com',
            'verified_email': True,
            'name': 'Jim Example',
            'given_name': 'Jim',
            'family_name': 'Example',
            'picture': 'https://image.com/image.png',
            'locale': 'en',
        },
        provider='google',
    )

    assert utils.get_social_account_image(account) == 'https://image.com/image.png'


def test_get_social_account_no_image_google():
    account = SocialAccount(
        extra_data={
            'id': '123',
            'email': 'jim@example.com',
            'verified_email': True,
            'name': 'Jim Example',
            'given_name': 'Jim',
            'family_name': 'Example',
            'locale': 'en',
        },
        provider='google',
    )

    assert utils.get_social_account_image(account) is None


def test_get_social_account_image_linkedin():
    account = SocialAccount(
        extra_data={
            'profilePicture': {
                'displayImage~': {
                    'paging': {'count': 10, 'start': 0, 'links': []},
                    'elements': [
                        {
                            'identifiers': [
                                {
                                    'identifier': 'https://image.com/image.png',
                                }
                            ]
                        },
                    ],
                }
            },
            'id': 's27gBbCPyF',
        },
        provider='linkedin_oauth2',
    )

    assert utils.get_social_account_image(account) == 'https://image.com/image.png'


def test_get_social_account_image_linkedin_no_profile_pic():
    account = SocialAccount(
        extra_data={'id': 's27gBbCPyF'},
        provider='linkedin_oauth2',
    )

    assert utils.get_social_account_image(account) is None


def test_get_social_account_image_linkedin_no_display_image():
    account = SocialAccount(
        extra_data={'profilePicture': {}, 'id': 's27gBbCPyF'},
        provider='linkedin_oauth2',
    )
    assert utils.get_social_account_image(account) is None


def test_get_social_account_image_linkedin_no_elements():
    account = SocialAccount(
        extra_data={
            'profilePicture': {'displayImage~': {'paging': {'count': 10, 'start': 0, 'links': []}, 'elements': []}},
            'id': 's27gBbCPyF',
        },
        provider='linkedin_oauth2',
    )
    assert utils.get_social_account_image(account) is None


@pytest.mark.django_db
def test_get_questionnaire_no_questions():
    user = UserFactory()
    questionnaire = utils.get_questionnaire(user, 'service')

    assert questionnaire is None


@pytest.mark.django_db
def test_get_questionnaire():
    user = UserFactory()
    service = ServiceFactory()
    first_question = QuestionFactory(service=service, id=0, name='in-progress', is_active=False)
    second_question = QuestionFactory(service=service, predefined_choices='TURNOVER_CHOICES')
    utils.set_questionnaire_answer(user, service.name, first_question.id, 'in-progress')

    questionnaire = utils.get_questionnaire(user, service.name)
    assert len(questionnaire['answers']) == 0
    assert len(questionnaire['questions']) == 1
    assert len(questionnaire['questions'][0]['choices']['options']) == 8

    utils.set_questionnaire_answer(user, service.name, second_question.id, 'answer')
    questionnaire = utils.get_questionnaire(user, service.name)
    assert len(questionnaire['answers']) == 1


@pytest.mark.django_db
def test_set_questionnaire_answer_invalid():
    user = UserFactory()

    assert utils.set_questionnaire_answer(user, 'service', 999, 'user_answer') is None
    assert utils.set_questionnaire_answer(user, 'service', 999, '') is None


@pytest.mark.django_db
def test_set_questionnaire_answer():
    user = UserFactory()
    service = ServiceFactory()
    question = QuestionFactory(service=service, name='in-progress')

    UserAnswerFactory(question=question, user=user)

    assert utils.set_questionnaire_answer(user, service.name, question.id, 'answer') is None

    question.name = 'continue'
    question.question_choices = {'options': [{'value': 'a', 'jump': 'end'}]}
    question.save()

    assert utils.set_questionnaire_answer(user, service.name, question.id, 'a') is None


@mock.patch('sso.user.utils.NotificationsAPIClient')
def test_notify_already_registered(mocked_notifications):
    utils.notify_already_registered('test@example.com')
    stub = mocked_notifications().send_email_notification
    assert stub.call_count == 1
    assert stub.call_args == mock.call(
        email_address='test@example.com',
        personalisation={
            'login_url': 'http://sso.trade.great:8003/accounts/login/',
            'password_reset_url': ('http://sso.trade.great:8003/accounts/password/reset/'),
            'contact_us_url': urls.domestic.CONTACT_US,
        },
        template_id='5c8cc5aa-a4f5-48ae-89e6-df5572c317ec',
    )
