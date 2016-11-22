from hashlib import sha256

from django.conf import settings
from django.utils.crypto import constant_time_compare


class SignatureRejection:

    @classmethod
    def generate_signature(self, secret, path, body):
        salt = bytes(secret, "utf-8")
        path = bytes(path, "utf-8")
        return sha256(path + body + salt).hexdigest()

    @classmethod
    def test_signature(self, request, secret=None):
        secret = secret or settings.PROXY_SIGNATURE_SECRET
        signature_header = settings.SIGNATURE_HEADERS.get(secret)
        signature_header_value = request.META.get(signature_header)

        if not signature_header_value:
            return False

        expected = self.generate_signature(
            secret,
            request.get_full_path(),
            request.body,
        )
        return constant_time_compare(expected, signature_header_value)
