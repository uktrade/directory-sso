import pytest
from unittest.mock import Mock

from sso.user.serializers import CreateUserProfileSerializer
from sso.user.serializers import CreateUserSerializer
from sso.user.tests.factories import UserFactory


@pytest.fixture()
def user():
    return UserFactory()


@pytest.mark.django_db
def test_createuserprofileserializer_deserialization(user):
    data = {'first_name': 'john',
            'last_name': 'smith',
            'mobile_phone_number': '0203044213',
            'job_title': 'Director',
            }
    request = Mock()
    request.user = user
    serializer = CreateUserProfileSerializer(
        data=data, context={'request': request}
    )
    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.first_name == data['first_name']
    assert instance.last_name == data['last_name']
    assert instance.job_title == data['job_title']
    assert instance.mobile_phone_number == data['mobile_phone_number']


@pytest.mark.django_db
def test_createuserserializer_deserialization():
    data = {'email': 'test@12345.com', 'password': 'Mypa11w0rd1'}
    serializer = CreateUserSerializer(data=data)
    assert serializer.is_valid()
    instance = serializer.save()

    assert instance.email == data['email']
    assert serializer.data['email'] == data['email']
    assert serializer.data['verification_code']


@pytest.mark.django_db
def test_createuserserializer_invalid_password_length():
    data = {'email': 'test@12345.com', 'password': 'AB123'}
    serializer = CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_createuserserializer_invalid_password_numeric():
    data = {'email': 'test@12345.com', 'password': '1234567891'}
    serializer = CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_createuserserializer_invalid_password_alpha():
    data = {'email': 'test@12345.com', 'password': 'ABCDEFGHIJK'}
    serializer = CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_createuserserializer_invalid_password_password():
    data = {'email': 'test@12345.com', 'password': '1passWord2'}
    serializer = CreateUserSerializer(data=data)
    assert not serializer.is_valid()
