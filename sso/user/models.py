from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class User(AbstractBaseUser):

    email = models.EmailField(
        _('email'),
        unique=True
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    # Field from django defining access to the admin
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates whether the user has superuser privileges.'
        ),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        # django method that must be implemented
        return self.email

    def get_short_name(self):
        # django method that must be implemented
        return self.email
