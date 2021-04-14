import pytest
from allauth.socialaccount.models import SocialAccount

from sso.user import utils
from sso.user.tests.factories import QuestionFactory, ServiceFactory, UserFactory


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
    QuestionFactory(service=service, id=0, name='in-progress', is_active=False)
    utils.set_questionnaire_answer(user, service.name, 0, 'in-progress')

    QuestionFactory(service=service, predefined_choices='TURNOVER_CHOICES')

    questionnaire = utils.get_questionnaire(user, service.name)
    assert len(questionnaire['answers']) == 0
    assert len(questionnaire['questions']) == 1
    assert len(questionnaire['questions'][0]['choices']['options']) == 8


@pytest.mark.django_db
def test_set_questionnaire_answer_invalid():
    user = UserFactory()

    assert utils.set_questionnaire_answer(user, 'service', 999, 'user_answer') is None


@pytest.mark.django_db
def test_set_questionnaire_answer():
    user = UserFactory()
    service = ServiceFactory()
    question = QuestionFactory(service=service, is_active=True)

    assert utils.set_questionnaire_answer(user, service.name, question.id, 'user_answer') is None
