from datetime import timedelta
from functools import partial

from django_cryptography.fields import encrypt

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from sso.api.model_utils import TimeStampedModel
from sso.user.models import User


class VerificationCode(TimeStampedModel):

    class Meta:
        ordering = ['-created']

    code = encrypt(models.CharField(
        max_length=128,
        default=partial(
            get_random_string,
            allowed_chars='0123456789',
            length=5
        ),
    ))
    user = models.OneToOneField(User, related_name='verification_code')
    date_verified = models.DateField(
        _('verified'),
        blank=True,
        null=True,
        help_text=_(
            'Designates whether this user has verified the code'
        ),
    )

    @property
    def expiration_date(self):
        return self.created + timedelta(days=settings.VERIFICATION_EXPIRY_DAYS)

    @property
    def is_expired(self):
        return now() >= self.expiration_date

    def __str__(self):
        return str(self.user)
