from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from sso.api.model_utils import TimeStampedModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields['is_staff'] is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields['is_superuser'] is not True:
            raise ValueError('Superuser must have is_superuser=True')

        user = self._create_user(email, password, **extra_fields)
        user.emailaddress_set.create(email=email, verified=True)
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):

    email = models.EmailField(
        _('email'),
        unique=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    utm = JSONField(
        blank=True,
        default={},
        help_text=_(
            'Urchin Tracking Module query parameters passed in the URL'
        ),
    )

    failed_login_attempts = models.PositiveSmallIntegerField(default=0)

    objects = UserManager()

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

    def check_password(self, raw_password):
        """Hook to update the failed login attempt counter."""
        is_correct = super().check_password(raw_password)
        if is_correct:
            self.failed_login_attempts = 0
            self.save()
        else:
            self.failed_login_attempts += 1
            self.save()
        self.notify_suspicious_login_activity()
        return is_correct

    def notify_suspicious_login_activity(self):
        notification_threshold = settings.SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS
        if (self.failed_login_attempts == notification_threshold and
                settings.SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL):
            body_message = "{user} tried to login {attempts} times".format(
                user=self.email,
                attempts=self.failed_login_attempts
            )
            send_mail(
                subject='Suspicious activity on SSO',
                message=body_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    settings.SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL
                ]
            )
