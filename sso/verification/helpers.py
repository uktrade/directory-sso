from functools import partial

from django.utils.crypto import get_random_string

generate_verification_code = partial(get_random_string, allowed_chars='0123456789', length=5)
