from django.http import HttpResponse

from signature.utils import SignatureRejection


class SignatureRejectionMiddleware(object):

    def process_request(self, request):
        if not SignatureRejection.test_signature(request):
            return HttpResponse('Unauthorized', status=401)
