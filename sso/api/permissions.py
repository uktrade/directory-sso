from django.conf import settings

from rest_framework import permissions

from signature.utils import SignatureRejection


class APIClientPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return SignatureRejection.test_signature(
            request, secret=settings.API_SIGNATURE_SECRET
        )
