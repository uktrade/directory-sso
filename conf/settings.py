import os
import ssl
from typing import Any, Dict
from pathlib import Path

import dj_database_url
import sentry_sdk
from django.urls import reverse_lazy
from django_log_formatter_asim import ASIMFormatter
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from conf.env import env
from core.helpers import is_valid_domain

from .utils import strip_password_data

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

APP_ENVIRONMENT = env.app_environment

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.debug

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

ALLOWED_IPS = [ip.strip() for ip in env.allowed_ips.split(',')]


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'clearcache',
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
    'django.middleware.cache.UpdateCacheMiddleware',
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
    'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'sso', 'templates'),
            Path(BASE_DIR) / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'header-bgs',
            Path(BASE_DIR) / 'node_modules' / '@uktrade' / 'great-design-system' / 'dist' / 'components' / 'footer-bgs',
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

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {'default': dj_database_url.config(default=env.database_url)}

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

STATIC_HOST = env.static_host
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = env.staticfiles_storage
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.secret_key

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
if env.sentry_dsn:
    sentry_sdk.init(
        dsn=env.sentry_dsn,
        environment=env.sentry_environment,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        before_send=strip_password_data,
        enable_tracing=env.sentry_enable_tracing,
        traces_sample_rate=env.sentry_traces_sample_rate,
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
FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.feature_enforce_staff_sso_enabled
# authbroker config
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS.append('authbroker_client.backends.AuthbrokerBackend')
    LOGIN_URL = reverse_lazy('authbroker_client:login')
    MIDDLEWARE.append('core.middleware.AdminPermissionCheckMiddleware')
else:
    LOGIN_URL = reverse_lazy('account_login')

# SSO config
AUTHBROKER_URL = env.staff_sso_authbroker_url
AUTHBROKER_CLIENT_ID = env.authbroker_client_id
AUTHBROKER_CLIENT_SECRET = env.authbroker_client_secret

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('oauth2_provider.contrib.rest_framework.OAuth2Authentication',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'UNAUTHENTICATED_USER': None,
    'PAGE_SIZE': env.rest_framework_page_size,
}

# django-oauth2-toolkit
OAUTH2_PROVIDER = {'SCOPES': {'profile': 'Access to your profile'}}
# https://github.com/jazzband/django-oauth-toolkit/issues/240
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'


# django-allauth
REDIRECT_FIELD_NAME = env.redirect_field_name
DEFAULT_REDIRECT_URL = env.default_redirect_url
LOGIN_REDIRECT_URL = DEFAULT_REDIRECT_URL
LOGOUT_REDIRECT_URL = env.logout_redirect_url
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_SUBJECT_PREFIX = env.account_email_subject_prefix
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env.account_default_http_protocol
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

VERIFICATION_EXPIRY_MINUTES = env.verification_expiry_minutes

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
}
EMAIL_BACKED_CLASS_NAME = env.email_backend_class_name
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.email_host
EMAIL_PORT = env.email_port
EMAIL_HOST_USER = env.email_host_user
EMAIL_HOST_PASSWORD = env.email_host_password
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.default_from_email

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

SESSION_COOKIE_DOMAIN = env.session_cookie_domain
# env var not same as setting to be more explicit (directory-ui uses same name)
SESSION_COOKIE_NAME = env.sso_session_cookie
SESSION_COOKIE_SECURE = env.session_cookie_secure

CSRF_COOKIE_SECURE = env.csrf_cookie_secure
CSRF_COOKIE_HTTPONLY = True

CSRF_TRUSTED_ORIGINS = env.csrf_trusted_origins
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS.split(',') if CSRF_TRUSTED_ORIGINS else []

# Set with comma separated values in env
ALLOWED_REDIRECT_DOMAINS = env.allowed_redirect_domains
ALLOWED_REDIRECT_DOMAINS = ALLOWED_REDIRECT_DOMAINS.split(',') if ALLOWED_REDIRECT_DOMAINS else []

for domain in ALLOWED_REDIRECT_DOMAINS:
    assert is_valid_domain(domain) is True

# Signature check
SIGNATURE_SECRET = env.signature_secret
SIGAUTH_URL_NAMES_WHITELIST = [
    'healthcheck',
    'healthcheck-ping',
    'pingdom',
    'activity-stream-users',
    'activity-stream-user-answers-vfm',
    'clearcache_admin',
]

SIGAUTH_NAMESPACE_WHITELIST = [
    'admin',
]

if DEBUG:
    # Whitelist debug_toolbar urls
    SIGAUTH_NAMESPACE_WHITELIST += ['djdt']

    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']
    if env.is_docker:
        import socket

        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + INTERNAL_IPS
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }

# api request key
DIRECTORY_API_SECRET = env.directory_api_secret

# Use proxy host name when generating links (e.g. in emails)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'

# Google tag manager
UTM_COOKIE_DOMAIN = env.utm_cookie_domain
GOOGLE_TAG_MANAGER_ID = env.google_tag_manager_id
GOOGLE_TAG_MANAGER_ENV = env.google_tag_manager_env

# sso profile
SSO_PROFILE_URL = env.sso_profile_url

# magna
MAGNA_URL = env.magna_url

# directory-api
DIRECTORY_API_CLIENT_BASE_URL = env.directory_api_client_base_url
DIRECTORY_API_CLIENT_API_KEY = env.directory_api_client_api_key
DIRECTORY_API_CLIENT_SENDER_ID = env.directory_api_client_sender_id
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = env.directory_api_client_default_timeout

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.directory_forms_api_base_url
DIRECTORY_FORMS_API_API_KEY = env.directory_forms_api_api_key
DIRECTORY_FORMS_API_SENDER_ID = env.directory_forms_api_sender_id
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.directory_forms_api_default_timeout
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.directory_forms_api_zendesk_sevice_name

# directory clients
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days

# Export Opportunities
EXOPS_APPLICATION_CLIENT_ID = env.exops_application_client_id

# HEADER AND FOOTER LINKS
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.directory_constants_url_great_domestic
DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES = env.directory_constants_url_export_opportunities
DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS = env.directory_constants_url_selling_online_overseas
DIRECTORY_CONSTANTS_URL_INVEST = env.directory_constants_url_invest
DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER = env.directory_constants_url_find_a_supplier
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.directory_constants_url_single_sign_on
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.directory_constants_url_find_a_buyer
DIRECTORY_CONSTANTS_URL_SSO_PROFILE = env.directory_constants_url_sso_profile
PRIVACY_COOKIE_DOMAIN = env.privacy_cookie_domain

# the following should be 5, but our auth backend are calling check_password
# twice, so we use 2*5
SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS = env.sso_suspicious_login_max_attempts
SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL = env.sso_suspicious_activity_notification_email

# Health check
DIRECTORY_HEALTHCHECK_TOKEN = env.health_check_token
DIRECTORY_HEALTHCHECK_BACKENDS = [
    # health_check.db.backends.DatabaseBackend
    # INSTALLED_APPS's health_check.db
]

GOV_NOTIFY_API_KEY = env.gov_notify_api_key
GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID = env.gov_notify_signup_confirmation_template_id
GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID = env.gov_notify_password_reset_template_id
GOV_NOTIFY_PASSWORD_RESET_UNVERIFIED_TEMPLATE_ID = env.gov_notify_password_reset_unverified_template_id
BGS_GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID = env.bgs_gov_notify_password_reset_template_id
BGS_GOV_NOTIFY_PASSWORD_RESET_UNVERIFIED_TEMPLATE_ID = env.bgs_gov_notify_password_reset_unverified_template_id
GOV_NOTIFY_SOCIAL_PASSWORD_RESET_TEMPLATE_ID = env.gov_notify_social_password_reset_template_id
GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.gov_notify_already_registered_template_id
GOV_NOTIFY_WELCOME_TEMPLATE_ID = env.gov_notify_welcome_template_id
GOV_NOTIFY_DATA_RETENTION_NOTIFICATION_TEMPLATE_ID = env.gov_notify_data_retention_notification_template_id

SSO_BASE_URL = env.sso_base_url

# Activity Stream
ACTIVITY_STREAM_IP_WHITELIST = env.activity_stream_ip_whitelist
# Defaults are not used so we don't accidentally expose the endpoint
# with default credentials
ACTIVITY_STREAM_ACCESS_KEY_ID = env.activity_stream_access_key_id
ACTIVITY_STREAM_SECRET_ACCESS_KEY = env.activity_stream_secret_access_key
ACTIVITY_STREAM_NONCE_EXPIRY_SECONDS = 60

# feature flags
FEATURE_FLAGS = {
    'SKIP_MIGRATE_ON': env.feature_skip_migrate,
    'DISABLE_REGISTRATION_ON': env.feature_disable_registration,
    'TEST_API_ON': env.feature_test_api_enabled,
    'TEST_API_EMAIL_DOMAIN': env.test_api_email_domain,
    'MAINTENANCE_MODE_ON': env.feature_maintenance_mode_enabled,  # used by directory-components
}

REDIS_URL = env.redis_url

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

CACHE_MIDDLEWARE_SECONDS = 60 * 30  # 30 minutes


SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ACCOUNT_SESSION_REMEMBER = True

# Admin restrictor
RESTRICT_ADMIN = env.ip_restrictor_restrict_ips
ALLOWED_ADMIN_IPS = env.ip_restrictor_allowed_admin_ips
ALLOWED_ADMIN_IPS = ALLOWED_ADMIN_IPS.split(',') if ALLOWED_ADMIN_IPS else []

ALLOWED_ADMIN_IP_RANGES = env.ip_restrictor_allowed_admin_ip_ranges
ALLOWED_ADMIN_IP_RANGES = ALLOWED_ADMIN_IP_RANGES.split(',') if ALLOWED_ADMIN_IP_RANGES else []

TRUST_PRIVATE_IP = True

# Directory Components
if env.feature_settings_janitor_enabled:
    INSTALLED_APPS.append('directory_components.janitor')
    DIRECTORY_COMPONENTS_VAULT_DOMAIN = env.directory_components_vault_domain
    DIRECTORY_COMPONENTS_VAULT_ROOT_PATH = env.directory_components_vault_root_path
    DIRECTORY_COMPONENTS_VAULT_PROJECT = env.directory_components_vault_project

# Provider specific settings
# These are stored in Django admin google/facebook

# Silence DRF's system check about having a global page size set without setting a global paginator. This is fine if we
# want case-by-case pagination but with a default page size.
SILENCED_SYSTEM_CHECKS = ["rest_framework.W001"]

# Celery
# is in api/celery.py
FEATURE_REDIS_USE_SSL = env.feature_redis_use_ssl
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = env.celery_task_always_eager
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None
CELERY_BROKER_USE_SSL = {'ssl_cert_reqs': ssl.CERT_NONE}
CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL

CELERY_IMPORTS = ('sso.tasks',)
# Flag for loading magna header
MAGNA_HEADER = env.magna_header
DIRECTORY_CONSTANTS_URL_GREAT_MAGNA = env.directory_constants_url_great_magna

# Data retention
DATA_RETENTION_STORAGE_YEARS = env.data_retention_storage_years

DATETIME_INPUT_FORMATS = ['%Y-%m-%d']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FEATURE_USE_BGS_TEMPLATES = env.feature_use_bgs_templates
