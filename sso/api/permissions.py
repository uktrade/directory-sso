from rest_framework import permissions

from sso.alice.utils import SignatureRejection


class APIClientPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return not SignatureRejection.test_signature(request)
