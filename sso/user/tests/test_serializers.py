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
    data = {'forename': 'john',
            'surname': 'smith',
            'phone': '0203044213',
            'job_title': 'Director',
            'is_official_representative': 'True',
            'is_background_checks_allowed': 'False',
            }
    request = Mock()
    request.user = user
    serializer = CreateUserProfileSerializer(
        data=data, context={'request': request}
    )
    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.forename == data['forename']
    assert instance.surname == data['surname']
    assert instance.job_title == data['job_title']
    assert instance.phone == data['phone']
    assert instance.is_official_representative == data[
        'is_official_representative'
    ]
    assert instance.is_background_checks_allowed == data[
        'is_background_checks_allowed'
    ]


@pytest.mark.django_db
def test_createuserserializer_deserialization():
    data = {'email': 'test@12345.com', 'password': 'mypassword'}
    serializer = CreateUserSerializer(data=data)
    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.email == data['email']
