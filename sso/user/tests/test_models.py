import pytest

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)

from sso.user.models import User


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
    user = User.objects.create_superuser(
        email='superuser@example.com', password='pass'
    )

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
    user = User.objects.create_superuser(
        email='superuser@example.com', password='pass'
    )

    assert user.password != 'pass'
    assert user.check_password('pass') is True


def test_user_model_has_update_create_timestamps():
    field_names = User._meta.get_all_field_names()

    assert 'created' in field_names
    created_field = User._meta.get_field_by_name('created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = User._meta.get_field_by_name('modified')[0]
    assert modified_field.__class__ is ModificationDateTimeField


def test_create_user():
    with pytest.raises(ValueError, message='Email must be set'):
        User.objects.create_user()


def test_create_superuser_not_staff():
    message = 'Superuser must have is_staff=True'
    with pytest.raises(ValueError, message=message):
        User.objects.create_superuser(
            is_staff=False, email=None, password=None,
        )


def test_create_superuser_not_superuser():
    message = 'Superuser must have is_superuser=True'
    with pytest.raises(ValueError, message=message):
        User.objects.create_superuser(
            is_superuser=False, email=None, password=None,
        )
