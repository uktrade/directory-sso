from datetime import timedelta

from django_cryptography.fields import encrypt

from django.conf import settings
from django.db import models
from django.utils.timezone import now

from sso.api.model_utils import TimeStampedModel
from sso.user.models import User
from sso.verification import helpers


class VerificationCode(TimeStampedModel):

    class Meta:
        ordering = ['-created']

    code = encrypt(models.CharField(
        max_length=128,
        default=helpers.generate_verification_code
    ))
    user = models.OneToOneField(User, related_name='verification_code', on_delete=models.CASCADE)
    date_verified = models.DateField(
        'verified',
        blank=True,
        null=True,
        help_text='Designates whether this user has verified the code',
    )

    @property
    def expiration_date(self):
        return self.created + timedelta(days=settings.VERIFICATION_EXPIRY_DAYS)

    @property
    def is_expired(self):
        return now() >= self.expiration_date

    def __str__(self):
        return str(self.user)
