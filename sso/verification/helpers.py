from functools import partial

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils.crypto import get_random_string


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp)


generate_verification_code = partial(get_random_string, allowed_chars='0123456789', length=5)

verification_token = TokenGenerator()
