from django.conf import settings
from django.test import TestCase, override_settings, RequestFactory

from rest_framework import status
from rest_framework.test import APIClient

from signature.middleware import SignatureRejectionMiddleware
from signature.utils import SignatureRejection
from signature.tests.client import SignatureTestClient


class BaseSignatureTestCase(TestCase):
    """
    Base TestCase providing a mock request and appropriate signature
    """

    def setUp(self):
        self.request = RequestFactory().get('/path')
        self.request._body = b'lol'
        # signature generated from the key in settings, and above path & body
        self.sig = (
            '25dc2f24f29c589a88baa22fa9aebbd58c5acb338f15ff920a752a9e414ba47e'
        )


class SignatureRejectionMiddlewareTestCase(BaseSignatureTestCase):

    def setUp(self):
        super().setUp()
        self.middleware = SignatureRejectionMiddleware()

    def test_generate_signature(self):
        signature = SignatureRejection.generate_signature(
            'secret',
            'path',
            b'body',
        )
        self.assertEqual(
            signature,
            'c6be1984f8b516e94d7257031cc47ed9863a433e461ac0117214b1b6a7801991',
        )

    @override_settings(UI_SECRET=SignatureTestClient.SECRET)
    def test_test_signature_missing(self):
        self.assertFalse(SignatureRejection.test_signature(self.request))

    @override_settings(UI_SECRET=SignatureTestClient.SECRET)
    def test_test_signature_incorrect(self):
        self.request.META['HTTP_X_SIGNATURE'] = 'bad-signature'
        self.assertFalse(SignatureRejection.test_signature(self.request))

    @override_settings(UI_SECRET=SignatureTestClient.SECRET)
    def test_test_signature_correct(self):
        self.request.META['HTTP_X_SIGNATURE'] = self.sig
        self.assertTrue(SignatureRejection.test_signature(self.request))

    @override_settings(UI_SECRET=SignatureTestClient.SECRET)
    def test_process_request_pass(self):
        self.request.META['HTTP_X_SIGNATURE'] = self.sig
        self.assertEqual(self.middleware.process_request(self.request), None)

    def test_process_request_fail(self):
        response = self.middleware.process_request(self.request)
        self.assertEqual(response.status_code, 401)


def test_urls_excluded_from_signature_check():
    client = APIClient()

    for url in settings.URLS_EXCLUDED_FROM_SIGNATURE_CHECK:
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
