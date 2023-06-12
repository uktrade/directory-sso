from django.conf import settings
from sigauth import middleware, permissions


class SignatureCheckMiddleware(middleware.SignatureCheckMiddlewareBase):
    secret = settings.SIGNATURE_SECRET


class SignatureCheckPermission(permissions.SignatureCheckPermissionBase):
    secret = settings.SIGNATURE_SECRET
    check_nonce = False
