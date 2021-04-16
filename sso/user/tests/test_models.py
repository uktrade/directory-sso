import pytest
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from sso.user.models import Question, User, UserAnswer, UserProfile
from sso.user.tests.factories import DataRetentionStatisticsFactory, QuestionFactory, ServiceFactory, UserFactory


@pytest.mark.django_db
def test_user_model_str():
    user = User(email='test@example.com', password='pass')

    assert user.email == str(user)


@pytest.mark.django_db
def test_user_model_get_full_name():
    user = User(email='test@example.com', password='pass')

    assert user.email == user.get_full_name()


@pytest.mark.django_db
def test_user_model_get_short_name():
    user = User(email='test@example.com', password='pass')

    assert user.email == user.get_short_name()


@pytest.mark.django_db
def test_user_manager_has_natural_key_method():
    expected = User.objects.create(email='test@example.com', password='pass')

    # NOTE: get_by_natural_key needs to exist for
    # `manage.py createsuperuser` to work
    user = User.objects.get_by_natural_key('test@example.com')

    assert user.email == 'test@example.com'
    assert user == expected


@pytest.mark.django_db
def test_user_manager_has_create_superuser_method():
    # NOTE: create_superuser needs to exist for
    # `manage.py createsuperuser` to work
    user = User.objects.create_superuser(email='superuser@example.com', password='pass')

    assert user.email == 'superuser@example.com'
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_user_manager_has_create_user_method():
    # NOTE: create_user needs to exist for
    # django's management commands to work
    user = User.objects.create_user(email='test@example.com', password='pass')

    assert user.email == 'test@example.com'
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_user_doesnt_save_plaintext_password():
    user = User.objects.create_user(email='test@example.com', password='pass')

    assert user.password != 'pass'
    assert user.check_password('pass') is True


@pytest.mark.django_db
def test_create_superuser_doesnt_save_plaintext_password():
    user = User.objects.create_superuser(email='superuser@example.com', password='pass')

    assert user.password != 'pass'
    assert user.check_password('pass') is True


def test_user_model_has_update_create_timestamps():
    field_names = [f.name for f in User._meta.get_fields()]

    assert 'created' in field_names
    created_field = User._meta.get_field('created')
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = User._meta.get_field('modified')
    assert modified_field.__class__ is ModificationDateTimeField


def test_create_user():
    with pytest.raises(ValueError):
        User.objects.create_user()


def test_create_superuser_not_staff():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            is_staff=False,
            email=None,
            password=None,
        )


def test_create_superuser_not_superuser():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            is_superuser=False,
            email=None,
            password=None,
        )


@pytest.mark.django_db
def test_create_user_profile():
    user = UserFactory()
    data = {
        'first_name': 'john',
        'last_name': 'smith',
        'mobile_phone_number': '0203044213',
        'job_title': 'Director',
        'user': user,
    }

    expected = UserProfile.objects.create(**data)
    assert expected.first_name == data['first_name']
    assert expected.last_name == data['last_name']
    assert expected.job_title == data['job_title']
    assert expected.mobile_phone_number == data['mobile_phone_number']
    assert str(expected) == str(user)


@pytest.mark.django_db
def test_datastastics_object():
    data = DataRetentionStatisticsFactory(sso_user=123)

    assert str(data) == '123'


@pytest.mark.django_db
def test_question_object():
    service = ServiceFactory()
    data = {'service': service, 'name': 'question'}

    expected = Question.objects.create(**data)

    assert str(expected) == data['name']
    assert expected.to_dict()['name'] == data['name']


@pytest.mark.django_db
def test_user_answer_object():
    user = UserFactory()
    question = QuestionFactory()
    data = {'user': user, 'question': question}

    expected = UserAnswer.objects.create(**data)

    assert str(expected) == str(f'{user} : {question}')
    assert expected.to_dict()['question_id'] == question.id
