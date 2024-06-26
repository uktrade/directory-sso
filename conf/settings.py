import os
import ssl
from typing import Any, Dict

import dj_database_url
import environ
import sentry_sdk
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from core.helpers import is_valid_domain
from .utils import strip_password_data

env = environ.Env()
for env_file in env.list('ENV_FILES', default=[]):
    env.read_env(f'conf/env/{env_file}')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.messages',
    'django_celery_beat',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'allauth.socialaccount.providers.google',
    'oauth2_provider',
    'rest_framework',
    'django_filters',
    'core',
    'sso',
    'sso.oauth2',
    'sso.user.apps.UserConfig',
    'sso.verification',
    'sso.testapi',
    'directory_constants',
    'health_check.db',
    'directory_healthcheck',
    'directory_components',
    'authbroker_client',
    'sort_order_field',
    'django_json_widget',
    'directory_forms_api_client',
]

SITE_ID = 1

MIDDLEWARE = [
    'directory_components.middleware.MaintenanceModeMiddleware',
    'core.middleware.SSODisplayLoggedInCookieMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'conf.signature.SignatureCheckMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'directory_components.middleware.NoCacheMiddlware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'sso', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sso.user.context_processors.redirect_next_processor',
                'directory_components.context_processors.feature_flags',
                'directory_components.context_processors.urls_processor',
                'directory_components.context_processors.header_footer_processor',
                'directory_components.context_processors.analytics',
                'directory_components.context_processors.cookie_notice',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

VCAP_SERVICES = env.json('VCAP_SERVICES', {})

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {'default': dj_database_url.config()}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_L10N = True

USE_TZ = True


# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATIC_HOST = env.str('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = env.str('STATICFILES_STORAGE', 'whitenoise.storage.CompressedStaticFilesStorage')
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# Logging for development
if DEBUG:
    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'}},
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'mohawk': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'factory': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
else:
    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'asim_formatter': {
                '()': ASIMFormatter,
            },
            'simple': {
                'style': '{',
                'format': '{asctime} {levelname} {message}',
            },
        },
        'handlers': {
            'asim': {
                'class': 'logging.StreamHandler',
                'formatter': 'asim_formatter',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['asim'],
                'level': 'INFO',
                'propagate': False,
            },
            'sentry_sdk': {
                'handlers': ['asim'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }

# Sentry
if env.str('SENTRY_DSN', ''):
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'),
        environment=env.str('SENTRY_ENVIRONMENT'),
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_password_data,
        enable_tracing=env.bool('SENTRY_ENABLE_TRACING', False),
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', 1.0),
    )

# Authentication
AUTH_USER_MODEL = 'user.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'directory_validators.password.AlphabeticPasswordValidator'},
    {'NAME': 'directory_validators.password.PasswordWordPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# SSO config
FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.bool('FEATURE_ENFORCE_STAFF_SSO_ENABLED', False)
# authbroker config
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS.append('authbroker_client.backends.AuthbrokerBackend')
    LOGIN_URL = reverse_lazy('authbroker_client:login')
    MIDDLEWARE.append('core.middleware.AdminPermissionCheckMiddleware')
else:
    LOGIN_URL = reverse_lazy('account_login')

# SSO config
AUTHBROKER_URL = env.str('STAFF_SSO_AUTHBROKER_URL')
AUTHBROKER_CLIENT_ID = env.str('AUTHBROKER_CLIENT_ID')
AUTHBROKER_CLIENT_SECRET = env.str('AUTHBROKER_CLIENT_SECRET')

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('oauth2_provider.contrib.rest_framework.OAuth2Authentication',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'UNAUTHENTICATED_USER': None,
    'PAGE_SIZE': env.int('REST_FRAMEWORK_PAGE_SIZE', 1000),
}

# django-oauth2-toolkit
OAUTH2_PROVIDER = {'SCOPES': {'profile': 'Access to your profile'}}
# https://github.com/jazzband/django-oauth-toolkit/issues/240
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'


# django-allauth
REDIRECT_FIELD_NAME = env.str('REDIRECT_FIELD_NAME', 'next')
DEFAULT_REDIRECT_URL = env.str('DEFAULT_REDIRECT_URL', 'https://find-a-buyer.export.great.gov.uk/')
LOGIN_REDIRECT_URL = env.str('LOGIN_REDIRECT_URL', DEFAULT_REDIRECT_URL)
LOGOUT_REDIRECT_URL = env.str('LOGOUT_REDIRECT_URL', DEFAULT_REDIRECT_URL)
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_SUBJECT_PREFIX = env.str('ACCOUNT_EMAIL_SUBJECT_PREFIX', 'Your great.gov.uk account: ')
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env.str('ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'https')
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # seconds
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_ADAPTER = 'sso.adapters.AccountAdapter'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
SOCIALACCOUNT_ADAPTER = 'sso.adapters.SocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = True

VERIFICATION_EXPIRY_MINUTES = env.int('VERIFICATION_EXPIRY_MINUTES', 30)

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
}
EMAIL_BACKED_CLASS_NAME = env.str('EMAIL_BACKEND_CLASS_NAME', 'default')
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_PORT = env.str('EMAIL_PORT')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL')

ACCOUNT_FORMS = {
    'signup': 'sso.user.forms.SignupForm',
    'login': 'sso.user.forms.LoginForm',
    'user': 'sso.user.forms.UserForm',
    'add_email': 'sso.user.forms.AddEmailForm',
    'account_change_password': 'sso.user.forms.ChangePasswordForm',
    'set_password': 'sso.user.forms.SetPasswordForm',
    'reset_password': 'sso.user.forms.ResetPasswordForm',
    'reset_password_from_key': 'sso.user.forms.ResetPasswordKeyForm',
}

SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN')
# env var not same as setting to be more explicit (directory-ui uses same name)
SESSION_COOKIE_NAME = env.str('SSO_SESSION_COOKIE')
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)

CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Set with comma separated values in env
ALLOWED_REDIRECT_DOMAINS = env.list('ALLOWED_REDIRECT_DOMAINS', default=[])
for domain in ALLOWED_REDIRECT_DOMAINS:
    assert is_valid_domain(domain) is True

# Signature check
SIGNATURE_SECRET = env.str('SIGNATURE_SECRET')
SIGAUTH_URL_NAMES_WHITELIST = [
    'healthcheck',
    'healthcheck-ping',
    'pingdom',
    'activity-stream-users',
    'activity-stream-user-answers-vfm',
]

# api request key
DIRECTORY_API_SECRET = env.str('DIRECTORY_API_SECRET', '')

# Use proxy host name when generating links (e.g. in emails)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'

# Google tag manager
UTM_COOKIE_DOMAIN = env.str('UTM_COOKIE_DOMAIN')
GOOGLE_TAG_MANAGER_ID = env.str('GOOGLE_TAG_MANAGER_ID')
GOOGLE_TAG_MANAGER_ENV = env.str('GOOGLE_TAG_MANAGER_ENV', '')

# sso profile
SSO_PROFILE_URL = env.str('SSO_PROFILE_URL')

# magna
MAGNA_URL = env.str('MAGNA_URL')

# directory-api
DIRECTORY_API_CLIENT_BASE_URL = env.str('DIRECTORY_API_CLIENT_BASE_URL')
DIRECTORY_API_CLIENT_API_KEY = env.str('DIRECTORY_API_CLIENT_API_KEY')
DIRECTORY_API_CLIENT_SENDER_ID = env.str('DIRECTORY_API_CLIENT_SENDER_ID', 'directory')
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = env.str('DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT', 15)

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int('DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5)
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.str('DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME', 'api')

# directory clients
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days

# Export Opportunities
EXOPS_APPLICATION_CLIENT_ID = env.str('EXOPS_APPLICATION_CLIENT_ID')

# HEADER AND FOOTER LINKS
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.str('DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', '')
DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES = env.str('DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES', '')
DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS = env.str('DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS', '')
DIRECTORY_CONSTANTS_URL_EVENTS = env.str('DIRECTORY_CONSTANTS_URL_EVENTS', '')
DIRECTORY_CONSTANTS_URL_INVEST = env.str('DIRECTORY_CONSTANTS_URL_INVEST', '')
DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER = env.str('DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER', '')
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.str('DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', '')
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.str('DIRECTORY_CONSTANTS_URL_FIND_A_BUYER', '')
DIRECTORY_CONSTANTS_URL_SSO_PROFILE = env.str('DIRECTORY_CONSTANTS_URL_SSO_PROFILE', '')
PRIVACY_COOKIE_DOMAIN = env.str('PRIVACY_COOKIE_DOMAIN')

# the following should be 5, but our auth backend are calling check_password
# twice, so we use 2*5
SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS = env.int('SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS', 10)
SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL = env.str('SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL', '')

# Health check
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    # health_check.db.backends.DatabaseBackend
    # INSTALLED_APPS's health_check.db
]

GOV_NOTIFY_API_KEY = env.str('GOV_NOTIFY_API_KEY')
GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID',
    '0c76b730-ac37-4b08-a8ba-7b34e4492853',
)
GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID', '9ef82687-4bc0-4278-b15c-a49bc9325b28'
)
GOV_NOTIFY_PASSWORD_RESET_UNVERIFIED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_PASSWORD_RESET_UNVERIFIED_TEMPLATE_ID', '6ad90342-6e55-4026-8884-b8a1d4d7f11c'
)
GOV_NOTIFY_SOCIAL_PASSWORD_RESET_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_SOCIAL_PASSWORD_RESET_TEMPLATE_ID', 'e5b5416d-854b-4aef-82da-865b6f901dbd'
)
GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID', '5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'
)
GOV_NOTIFY_WELCOME_TEMPLATE_ID = env.str('GOV_NOTIFY_WELCOME_TEMPLATE_ID', '0a4ae7a9-7f67-4f5d-a536-54df2dee42df')
GOV_NOTIFY_DATA_RETENTION_NOTIFICATION_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_DATA_RETENTION_NOTIFICATION_TEMPLATE_ID', '39e44eaa-515f-4843-b7c5-d3dd5d86747c'
)

SSO_BASE_URL = env.str('SSO_BASE_URL', 'https://sso.trade.great.gov.uk')

# Activity Stream
ACTIVITY_STREAM_IP_WHITELIST = env.str('ACTIVITY_STREAM_IP_WHITELIST', '')
# Defaults are not used so we don't accidentally expose the endpoint
# with default credentials
ACTIVITY_STREAM_ACCESS_KEY_ID = env.str('ACTIVITY_STREAM_ACCESS_KEY_ID')
ACTIVITY_STREAM_SECRET_ACCESS_KEY = env.str('ACTIVITY_STREAM_SECRET_ACCESS_KEY')
ACTIVITY_STREAM_NONCE_EXPIRY_SECONDS = 60

# feature flags
FEATURE_FLAGS = {
    'SKIP_MIGRATE_ON': env.bool('FEATURE_SKIP_MIGRATE', False),
    'DISABLE_REGISTRATION_ON': env.bool('FEATURE_DISABLE_REGISTRATION', False),
    'TEST_API_ON': env.bool('FEATURE_TEST_API_ENABLED', False),
    'TEST_API_EMAIL_DOMAIN': env.str('TEST_API_EMAIL_DOMAIN', 'ci.uktrade.io'),
    'MAINTENANCE_MODE_ON': env.bool('FEATURE_MAINTENANCE_MODE_ENABLED', False),  # used by directory-components
}


VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL')

cache = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': REDIS_URL,
    'OPTIONS': {
        'CLIENT_CLASS': "django_redis.client.DefaultClient",
    },
}

CACHES = {
    'default': cache,
    'api_fallback': cache,
}


SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ACCOUNT_SESSION_REMEMBER = True

# Admin restrictor
RESTRICT_ADMIN = env.bool('IP_RESTRICTOR_RESTRICT_IPS', False)
ALLOWED_ADMIN_IPS = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IP_RANGES', default=[])
TRUST_PRIVATE_IP = True

# Directory Components
if env.bool('FEATURE_SETTINGS_JANITOR_ENABLED', False):
    INSTALLED_APPS.append('directory_components.janitor')
    DIRECTORY_COMPONENTS_VAULT_DOMAIN = env.str('DIRECTORY_COMPONENTS_VAULT_DOMAIN')
    DIRECTORY_COMPONENTS_VAULT_ROOT_PATH = env.str('DIRECTORY_COMPONENTS_VAULT_ROOT_PATH')
    DIRECTORY_COMPONENTS_VAULT_PROJECT = env.str('DIRECTORY_COMPONENTS_VAULT_PROJECT')

# Provider specific settings
# These are stored in Django admin google/facebook

# Silence DRF's system check about having a global page size set without setting a global paginator. This is fine if we
# want case-by-case pagination but with a default page size.
SILENCED_SYSTEM_CHECKS = ["rest_framework.W001"]

# Celery
# is in api/celery.py
FEATURE_REDIS_USE_SSL = env.bool('FEATURE_REDIS_USE_SSL', False)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', False)
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None
CELERY_BROKER_USE_SSL = {'ssl_cert_reqs': ssl.CERT_NONE}
CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL

CELERY_IMPORTS = ('sso.tasks',)
# Flag for loading magna header
MAGNA_HEADER = env.bool('MAGNA_HEADER', False)
DIRECTORY_CONSTANTS_URL_GREAT_MAGNA = env.str('DIRECTORY_CONSTANTS_URL_GREAT_MAGNA', 'https://great.gov.uk/')

# Data retention
DATA_RETENTION_STORAGE_YEARS = env.int('DATA_RETENTION_STORAGE_YEARS', 3)

DATETIME_INPUT_FORMATS = ['%Y-%m-%d']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
