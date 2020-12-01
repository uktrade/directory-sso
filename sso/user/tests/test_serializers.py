import pytest

from sso.user import serializers
from sso.user.tests import factories


@pytest.mark.django_db
def test_user_profile_serializer_deserialization(rf):
    data = {
        'first_name': 'john',
        'last_name': 'smith',
        'mobile_phone_number': '0203044213',
        'job_title': 'Director',
    }
    request = rf.get('/')
    request.user = factories.UserFactory.create()
    serializer = serializers.UserProfileSerializer(data=data, context={'request': request})
    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.first_name == data['first_name']
    assert instance.last_name == data['last_name']
    assert instance.job_title == data['job_title']
    assert instance.mobile_phone_number == data['mobile_phone_number']


@pytest.mark.django_db
def test_createuserserializer_deserialization():
    data = {'email': 'test@12345.com', 'password': 'Mypa11w0rd1'}
    serializer = serializers.CreateUserSerializer(data=data)
    assert serializer.is_valid()
    instance = serializer.save()

    assert instance.email == data['email']
    assert serializer.data['email'] == data['email']
    assert serializer.data['verification_code']


@pytest.mark.django_db
def test_createuserserializer_invalid_password_length():
    data = {'email': 'test@12345.com', 'password': 'AB123'}
    serializer = serializers.CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_createuserserializer_invalid_password_numeric():
    data = {'email': 'test@12345.com', 'password': '1234567891'}
    serializer = serializers.CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_createuserserializer_invalid_password_alpha():
    data = {'email': 'test@12345.com', 'password': 'ABCDEFGHIJK'}
    serializer = serializers.CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_createuserserializer_invalid_password_password():
    data = {'email': 'test@12345.com', 'password': '1passWord2'}
    serializer = serializers.CreateUserSerializer(data=data)
    assert not serializer.is_valid()


@pytest.mark.django_db
def test_user_serializer_no_profile():
    user = factories.UserFactory.create()
    serializer = serializers.UserSerializer(user)

    assert serializer.data['user_profile'] is None


@pytest.mark.django_db
def test_user_serializer_has_profile():
    user_profile = factories.UserProfileFactory.create()
    serializer = serializers.UserSerializer(user_profile.user)

    assert serializer.data['user_profile'] == serializers.UserProfileSerializer(user_profile).data
