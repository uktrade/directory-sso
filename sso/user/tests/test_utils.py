import pytest
from allauth.socialaccount.models import SocialAccount

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


@pytest.mark.django_db
def test_path_get():
    dict1 = {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': 'v22'}}
    assert utils.path_get(dict1, '') == dict1
    assert utils.path_get(dict1, None) == dict1
    assert utils.path_get(dict1, 'k1') == 'v1'
    assert utils.path_get(dict1, 'k2.k22') == 'v22'
    assert utils.path_get(dict1, 'k2') == {'k21': 'v21', 'k22': 'v22'}
    assert utils.path_get(dict1, 'wrong') is None
    assert utils.path_get(dict1, 'k2.wrong') is None


@pytest.mark.django_db
def test_path_replace():
    dict1 = {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': 'v22'}}
    assert utils.path_replace(dict1, '', {'r': 'r'}) == {'r': 'r'}
    assert utils.path_replace(dict1, 'k1', {'r': 'r'}) == {'k1': {'r': 'r'}, 'k2': {'k21': 'v21', 'k22': 'v22'}}
    assert utils.path_replace(dict1, 'k2', {'r': 'r'}) == {'k1': 'v1', 'k2': {'r': 'r'}}
    assert utils.path_replace(dict1, 'k2.k22', {'r': 'r'}) == {'k1': 'v1', 'k2': {'k21': 'v21', 'k22': {'r': 'r'}}}
    assert utils.path_replace(dict1, 'new', {'r': 'r'}) == {
        'new': {'r': 'r'},
        'k1': 'v1',
        'k2': {'k21': 'v21', 'k22': 'v22'},
    }
    assert utils.path_replace(dict1, 'k2.new', {'r': 'r'}) == {
        'k1': 'v1',
        'k2': {'k21': 'v21', 'k22': 'v22', 'new': {'r': 'r'}},
    }
    assert utils.path_replace(dict1, 'new1.new2.new3', {'r': 'r'}) == {
        'k1': 'v1',
        'k2': {'k21': 'v21', 'k22': 'v22'},
        'new1': {'new2': {'new3': {'r': 'r'}}},
    }
    assert utils.path_replace(dict1, 'k2.k22.new', {'r': 'r'}) == {
        'k1': 'v1',
        'k2': {'k21': 'v21', 'k22': {'new': {'r': 'r'}}},
    }
    assert utils.path_replace(dict1, '', None) == {}
    assert utils.path_replace(dict1, 'k1', None) == {'k1': None, 'k2': {'k21': 'v21', 'k22': 'v22'}}
    assert utils.path_replace(dict1, 'k2', None) == {'k1': 'v1', 'k2': None}
