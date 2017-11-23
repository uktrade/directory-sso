import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


@pytest.mark.parametrize(
    'password',
    (
        'ABCDEFGHILM',
        '1234567890',
        'passwordpassword',
        'J[t2xT'
    )
)
def test_invalid_password(password):
    with pytest.raises(ValidationError):
        validate_password(password=password)


@pytest.mark.parametrize(
    'password',
    (
        'ABCDE12345',
        '6yUu9QrmFR'
    )
)
def test_valid_password(password):
    assert validate_password(password=password) is None
