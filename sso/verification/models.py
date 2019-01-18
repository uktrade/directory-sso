from datetime import datetime
from functools import partial

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django_cryptography.fields import encrypt

from sso.api.model_utils import TimeStampedModel


class VerificationCode(TimeStampedModel):

    class Meta:
        ordering = ['-created']

    code = encrypt(models.CharField(
        max_length=128,
        default=partial(get_random_string, length=16),
    ))

    user_id = models.IntegerField(
        null=True,
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
            'Designates whether this user has verified the code'
        ),
    )

    @property
    def is_expired(self):
        return (datetime.utcnow() - self.created).days > self.expiry_days

    @property
    def expiry_days(self):
        return settings.VERIFICATION_EXPIRY_DAYS

    def __str__(self):
        return self.code
