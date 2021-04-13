from allauth.account.forms import default_token_generator, user_pk_to_url_str
from allauth.account.models import EmailConfirmation
from directory_constants import choices
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from sort_order_field import SortOrderField

from sso.api.model_utils import TimeStampedModel
from sso.constants import API_DATETIME_FORMAT


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

    email = models.EmailField(_('email'), unique=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    utm = JSONField(blank=True, default=dict, help_text=_('Urchin Tracking Module query parameters passed in the URL'))
    hashed_uuid = models.CharField(max_length=200, help_text='a hash representation of the object\'s id', default='')

    first_name = models.CharField(max_length=30, blank=True)

    last_name = models.CharField(max_length=30, blank=True)

    failed_login_attempts = models.PositiveSmallIntegerField(default=0)

    inactivity_notification = models.PositiveSmallIntegerField(default=0)

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
            # if user is logged in then set inactivity to default (0)
            self.inactivity_notification = 0
            self.save()
        else:
            self.failed_login_attempts += 1
            self.save()
        self.notify_suspicious_login_activity()
        return is_correct

    def notify_suspicious_login_activity(self):
        notification_threshold = settings.SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS
        if self.failed_login_attempts == notification_threshold and settings.SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL:
            body_message = "{user} tried to login {attempts} times".format(
                user=self.email, attempts=self.failed_login_attempts
            )
            send_mail(
                subject='Suspicious activity on SSO',
                message=body_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL],
            )

    def get_password_reset_link(self):
        return reverse(
            "account_reset_password_from_key",
            kwargs={'uidb36': user_pk_to_url_str(self), 'key': default_token_generator.make_token(self)},
        )

    def get_email_verification_link(self):
        email_address = self.emailaddress_set.last()
        email_confirmation = EmailConfirmation.create(email_address)
        email_confirmation.sent = timezone.now()
        email_confirmation.save()

        return reverse("account_confirm_email", args=[email_confirmation.key])


class UserProfile(TimeStampedModel):
    # TODO: move these over to directory-constants
    CORE_SEGMENTS = [
        ('SUSTAIN', 'Sustain'),
        ('REASSURE', 'Reassure'),
        ('PROMOTE', 'Promote'),
        ('CHALLENGE', 'Challenge'),
    ]

    class Meta:
        ordering = ['-created']

    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    job_title = models.CharField(max_length=128, blank=True, null=True)
    mobile_phone_number = models.CharField(max_length=128, blank=True, null=True)
    segment = models.CharField(max_length=15, choices=CORE_SEGMENTS, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class DataRetentionStatistics(TimeStampedModel):
    sso_user = models.IntegerField(blank=True, null=True)
    company_user = models.IntegerField(blank=True, null=True)
    company = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _('Data Retention Statistics')
        verbose_name_plural = _('Data Retention Statistics')

    def __str__(self):
        return str(self.sso_user)


class Service(TimeStampedModel):
    # a service name e.g. great-cms
    name = models.CharField(max_length=128)


class ServicePage(TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_pages')
    page_name = models.CharField(max_length=128)

    class Meta:
        indexes = [models.Index(fields=['service'])]
        unique_together = [['service', 'page_name']]


class UserPageView(TimeStampedModel):
    # Records an instance of a user reading a page ONCE. Subsequent reads will add extra records
    service_page = models.ForeignKey(ServicePage, on_delete=models.CASCADE, related_name='page_views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_views')

    class Meta:
        unique_together = [['user', 'service_page']]

    def to_dict(self):
        return {
            'service': self.service_page.service.name,
            'page': self.service_page.page_name,
            'modified': self.modified.strftime(API_DATETIME_FORMAT),
            'created': self.created.strftime(API_DATETIME_FORMAT),
        }


class LessonCompleted(TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    lesson_page = models.CharField(max_length=255)
    lesson = models.IntegerField()
    module = models.IntegerField()  # Saving PK so it can be queried
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['user', 'lesson']]

    def to_dict(self):
        return {
            'service': self.service.name,
            'lesson_page': self.lesson_page,
            'lesson': self.lesson,
            'module': self.module,
            'user': self.user.id,
            'modified': self.modified.strftime(API_DATETIME_FORMAT),
            'created': self.created.strftime(API_DATETIME_FORMAT),
        }


QUESTION_TYPES = [
    ('RADIO', 'radio'),
    ('SELECTION', 'Selection'),
    ('MULTIPLE_SELECTOR', 'Multiple selection'),
    ('TEXT', 'text'),
    ('COMPANY_LOOKUP', 'Company lookup'),
]


PREDEFINED_CHOICES = [
    ('EXPERTISE_REGION_CHOICES', 'EXPERTISE_REGION_CHOICES'),
    ('TURNOVER_CHOICES', 'TURNOVER_CHOICES'),
]


class Question(TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=256)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_choices = JSONField(blank=True, default=dict, help_text=_('Question parameters'))
    predefined_choices = models.CharField(blank=True, null=True, max_length=128, choices=PREDEFINED_CHOICES)
    is_active = models.BooleanField(default=True)
    sort_order = SortOrderField(_("Sort"))

    class Meta:
        ordering = ('sort_order',)

    def __str__(self):
        return str(self.name)

    def to_dict(self):
        question_options = (
            [{'label': label, 'value': value} for value, label in choices.__dict__.get(self.predefined_choices, [])]
            if self.predefined_choices
            else []
        )
        question_choices = self.question_choices or {'options': []}
        if question_options:
            question_choices['options'] = question_choices.get('options', []) + question_options
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'type': self.question_type,
            'choices': question_choices,
            'order': self.sort_order,
        }


class UserAnswer(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = JSONField(blank=True, default=dict)

    def to_dict(self):
        return {'question_id': self.question.id, 'answer': self.answer}

    def __str__(self):
        return str(f'{self.user}:{self.question.name}')
