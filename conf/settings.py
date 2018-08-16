import json
import os

import dj_database_url
import environ
import rediscluster

from django.urls import reverse_lazy

from core.helpers import is_valid_domain


env = environ.Env()

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
    'raven.contrib.django.raven_compat',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'oauth2_provider',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'core',
    'sso',
    'sso.oauth2',
    'sso.user.apps.UserConfig',
    'sso.testapi',
    'directory_constants',
    'directory_healthcheck',
    'health_check',
    'health_check.db',
    'directory_components',
    'export_elements',
    'rediscluster',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'directory_components.middleware.MaintenanceModeMiddleware',
    'core.middleware.SSODisplayLoggedInCookieMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'conf.signature.SignatureCheckMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'admin_ip_restrictor.middleware.AdminIPRestrictorMiddleware',
    'directory_components.middleware.NoCacheMiddlware',
    'directory_components.middleware.RobotsIndexControlHeaderMiddlware',
]

CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', False)

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
                'sso.user.context_processors.redirect_next_processor',
                'directory_components.context_processors.feature_flags',
                'directory_components.context_processors.urls_processor',
                ('directory_components.context_processors.'
                 'header_footer_processor'),
                'directory_components.context_processors.analytics',
                'directory_components.context_processors.cookie_notice',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
        },
    },
]


WSGI_APPLICATION = 'conf.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config()
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# Sentry
RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN', ''),
}


# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
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
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

# Authentication
AUTH_USER_MODEL = 'user.User'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.MinimumLengthValidator'
        ),
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'directory_validators.password_validation.'
                'AlphabeticPasswordValidator'
    },
    {
        'NAME': 'directory_validators.password_validation.'
                'PasswordWordPasswordValidator'
    }
]


AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'UNAUTHENTICATED_USER': None,
}

# django-oauth2-toolkit
OAUTH2_PROVIDER = {
    'SCOPES': {
        'profile': 'Access to your profile'
    }
}

# django-allauth
REDIRECT_FIELD_NAME = env.str(
    'REDIRECT_FIELD_NAME', 'next'
)
DEFAULT_REDIRECT_URL = env.str(
    'DEFAULT_REDIRECT_URL', 'https://find-a-buyer.export.great.gov.uk/'
)
LOGIN_REDIRECT_URL = env.str(
    'LOGIN_REDIRECT_URL', DEFAULT_REDIRECT_URL
)
LOGOUT_REDIRECT_URL = env.str(
    'LOGOUT_REDIRECT_URL', DEFAULT_REDIRECT_URL
)
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_SUBJECT_PREFIX = env.str(
    'ACCOUNT_EMAIL_SUBJECT_PREFIX', 'Your great.gov.uk account: '
)
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env.str(
    'ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'https'
)
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # seconds
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_ADAPTER = 'sso.adapters.AccountAdapter'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend'
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
    'change_password': 'sso.user.forms.ChangePasswordForm',
    'set_password': 'sso.user.forms.SetPasswordForm',
    'reset_password': 'sso.user.forms.ResetPasswordForm',
    'reset_password_from_key': 'sso.user.forms.ResetPasswordKeyForm',
}

SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN')
# env var not same as setting to be more explicit (directory-ui uses same name)
SESSION_COOKIE_NAME = env.str('SSO_SESSION_COOKIE')
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)

# Set with comma separated values in env
ALLOWED_REDIRECT_DOMAINS = env.list('ALLOWED_REDIRECT_DOMAINS', default=[])
for domain in ALLOWED_REDIRECT_DOMAINS:
    assert is_valid_domain(domain) is True

# Signature check
SIGNATURE_SECRET = env.str('SIGNATURE_SECRET')

URLS_EXCLUDED_FROM_SIGNATURE_CHECK = [
    reverse_lazy('health-check-database')
]

# Use proxy host name when generating links (e.g. in emails)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', True)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Google tag manager
UTM_COOKIE_DOMAIN = env.str('UTM_COOKIE_DOMAIN')
GOOGLE_TAG_MANAGER_ID = env.str('GOOGLE_TAG_MANAGER_ID')
GOOGLE_TAG_MANAGER_ENV = env.str('GOOGLE_TAG_MANAGER_ENV', '')

# sso profile
SSO_PROFILE_URL = env.str('SSO_PROFILE_URL')

HEADER_FOOTER_CONTACT_US_URL = env.str(
    'HEADER_FOOTER_CONTACT_US_URL',
    'https://contact-us.export.great.gov.uk/directory',
)

FEEDBACK_FORM_URL = env.str(
    'SSO_FEEDBACK_FORM_URL',
    'https://contact-us.export.great.gov.uk/feedback/directory/'
)

# directory-external-api
DIRECTORY_API_EXTERNAL_CLIENT_CLASSES = {
    'default': 'directory_api_external.client.DirectoryAPIExternalClient',
    'unit-test': (
        'directory_api_external.dummy_client.DummyDirectoryAPIExternalClient'
    ),
}
DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME = env.str(
    'DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME', 'default'
)
DIRECTORY_API_EXTERNAL_CLIENT_CLASS = DIRECTORY_API_EXTERNAL_CLIENT_CLASSES[
    DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME
]
DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET = env.str(
    'DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET'
)
DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL = env.str(
    'DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL'
)

# Export Opportunities
EXOPS_APPLICATION_CLIENT_ID = env.str('EXOPS_APPLICATION_CLIENT_ID')

# HEADER AND FOOTER LINKS
HEADER_FOOTER_URLS_GREAT_HOME = env.str('HEADER_FOOTER_URLS_GREAT_HOME', '')
HEADER_FOOTER_URLS_FAB = env.str('HEADER_FOOTER_URLS_FAB', '')
HEADER_FOOTER_URLS_SOO = env.str('HEADER_FOOTER_URLS_SOO', '')
HEADER_FOOTER_URLS_EVENTS = env.str('HEADER_FOOTER_URLS_EVENTS', '')
HEADER_FOOTER_URLS_CONTACT_US = env.str('HEADER_FOOTER_URLS_CONTACT_US', '')
HEADER_FOOTER_URLS_DIT = env.str('HEADER_FOOTER_URLS_DIT', '')
PRIVACY_COOKIE_DOMAIN = env.str('PRIVACY_COOKIE_DOMAIN')

# the following should be 5, but our auth backend are calling check_password
# twice, so we use 2*5
SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS = env.int(
    'SSO_SUSPICIOUS_LOGIN_MAX_ATTEMPTS',
    10
)
SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL = env.str(
    'SSO_SUSPICIOUS_ACTIVITY_NOTIFICATION_EMAIL',
    ''
)

# Health check
HEALTH_CHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')

GOV_NOTIFY_API_KEY = env.str('GOV_NOTIFY_API_KEY')
GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_SIGNUP_CONFIRMATION_TEMPLATE_ID',
    '0c76b730-ac37-4b08-a8ba-7b34e4492853',
)
GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_PASSWORD_RESET_TEMPLATE_ID',
    '9ef82687-4bc0-4278-b15c-a49bc9325b28'
)
GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID = env.str(
    'GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID',
    '5c8cc5aa-a4f5-48ae-89e6-df5572c317ec'
    )

# Admin restrictor
RESTRICT_ADMIN = env.str('RESTRICT_ADMIN', False)
ALLOWED_ADMIN_IPS = env.list('ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list('ALLOWED_ADMIN_IP_RANGES', default=[])

SSO_BASE_URL = env.str('SSO_BASE_URL', 'https://sso.trade.great.gov.uk')

# Activity Stream
ACTIVITY_STREAM_IP_WHITELIST = env.str('ACTIVITY_STREAM_IP_WHITELIST', '')
# Defaults are not used so we don't accidentally expose the endpoint
# with default credentials
ACTIVITY_STREAM_ACCESS_KEY_ID = env.str(
    'ACTIVITY_STREAM_ACCESS_KEY_ID'
)
ACTIVITY_STREAM_SECRET_ACCESS_KEY = env.str(
    'ACTIVITY_STREAM_SECRET_ACCESS_KEY'
)
ACTIVITY_STREAM_NONCE_EXPIRY_SECONDS = 60

# feature flags
FEATURE_FLAGS = {
    'USER_CACHE_ON': env.bool('FEATURE_CACHE_ENABLED', False),
    'ACTIVITY_STREAM_NONCE_CACHE_ON': env.bool(
        'FEATURE_ACTIVITY_STREAM_NONCE_CACHE_ENABLED', False
    ),
    'SKIP_MIGRATE_ON': env.bool('FEATURE_SKIP_MIGRATE', False),
    'DISABLE_REGISTRATION_ON': env.bool('FEATURE_DISABLE_REGISTRATION', False),
    'TEST_API_ON': env.bool('FEATURE_TEST_API_ENABLED', False),
    # used by directory-components
    'SEARCH_ENGINE_INDEXING_OFF': env.bool(
        'FEATURE_SEARCH_ENGINE_INDEXING_DISABLED', False
    ),
    # used by directory-components
    'MAINTENANCE_MODE_ON': env.bool('FEATURE_MAINTENANCE_MODE_ENABLED', False),
}

CACHE_BACKENDS = {
    'redis': 'django_redis.cache.RedisCache',
    'dummy': 'django.core.cache.backends.dummy.DummyCache',
    'locmem': 'django.core.cache.backends.locmem.LocMemCache'
}

CACHES = {}

if FEATURE_FLAGS['USER_CACHE_ON']:
    CACHES['default'] = {
        'BACKEND': CACHE_BACKENDS[os.getenv('CACHE_BACKEND', 'redis')],
        'LOCATION': os.getenv('REDIS_URL')
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
else:
    CACHES['default'] = {
        'BACKEND': CACHE_BACKENDS['locmem'],
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

if FEATURE_FLAGS['ACTIVITY_STREAM_NONCE_CACHE_ON']:
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    redis_credentials = vcap_services['redis'][0]['credentials']

    # rediscluster, by default, breaks if using the combination of
    # - rediss:// connection uri
    # - skip_full_coverage_check=True
    # We work around the issues by forcing the uri to start with redis://
    # and setting the connection class to use SSL if necessary
    is_tls_enabled = redis_credentials['uri'].startswith('rediss://')
    if is_tls_enabled:
        redis_uri = redis_credentials['uri'].replace('rediss://', 'redis://')
        redis_connection_class = rediscluster.connection.SSLClusterConnection
    else:
        redis_uri = redis_credentials['uri']
        redis_connection_class = rediscluster.connection.ClusterConnection

    CACHES['activity_stream_nonce'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': redis_uri,
        'OPTIONS': {
            'REDIS_CLIENT_CLASS': 'rediscluster.StrictRedisCluster',
            'REDIS_CLIENT_KWARGS': {
                'decode_responses': True,
            },
            'CONNECTION_POOL_CLASS':
                'rediscluster.connection.ClusterConnectionPool',
            'CONNECTION_POOL_KWARGS': {
                # AWS ElasticCache disables CONFIG commands
                'skip_full_coverage_check': True,
                'connection_class': redis_connection_class,
            },
        },
        'KEY_PREFIX': 'directory-sso-activity-stream-nonce',
    }
