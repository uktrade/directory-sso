from sigauth import middleware, permissions

from django.conf import settings


class SignatureCheckMiddleware(middleware.SignatureCheckMiddlewareBase):
    secret = settings.SIGNATURE_SECRET


class SignatureCheckPermission(permissions.SignatureCheckPermissionBase):
    secret = settings.SIGNATURE_SECRET
