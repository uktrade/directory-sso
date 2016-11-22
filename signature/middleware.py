from django.conf import settings
from django.http import HttpResponse

from signature.utils import SignatureRejection


class SignatureRejectionMiddleware(object):

    def process_request(self, request):
        path = request.get_full_path()

        if path not in settings.URLS_EXCLUDED_FROM_SIGNATURE_CHECK:
            if not SignatureRejection.test_signature(request):
                return HttpResponse('Unauthorized', status=401)
