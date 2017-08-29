import os

import dj_database_url

from .helpers import is_valid_domain

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if (os.getenv('DEBUG') == 'true') else False

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
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
    'sso',
    'sso.oauth2',
    'sso.user.apps.UserConfig',
    'directory_constants',
    'directory_header_footer',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'config.middleware.SSODisplayLoggedInCookieMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'config.signature.SignatureCheckMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True if (
    os.getenv('CORS_ORIGIN_ALLOW_ALL') == 'true'
) else False


ROOT_URLCONF = 'config.urls'

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
                'sso.context_processors.analytics',
                'sso.context_processors.feature_flags',
                ('directory_header_footer.context_processors.'
                 'header_footer_context_processor'),
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'

# Redis cache enabled
FEATURE_REDIS_CACHE_ENABLED = os.getenv(
    'FEATURE_REDIS_CACHE_ENABLED') == 'true'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config()
}

CACHE_BACKENDS = {
    'redis': 'django_redis.cache.RedisCache',
    'dummy': 'django.core.cache.backends.dummy.DummyCache',
    'locmem': 'django.core.cache.backends.locmem.LocMemCache'
}
CACHES = {
    'default': {
        'BACKEND': CACHE_BACKENDS[os.getenv('CACHE_BACKEND', 'redis')],
        'LOCATION': os.getenv('REDIS_URL')
    }
}

if FEATURE_REDIS_CACHE_ENABLED:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


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

STATIC_HOST = os.environ.get('STATIC_HOST', '')
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
SECRET_KEY = os.environ["SECRET_KEY"]

# Sentry
RAVEN_CONFIG = {
    "dsn": os.getenv("SENTRY_DSN"),
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
REDIRECT_FIELD_NAME = os.getenv(
    'REDIRECT_FIELD_NAME', 'next'
)
DEFAULT_REDIRECT_URL = os.getenv(
    'DEFAULT_REDIRECT_URL', 'https://find-a-buyer.export.great.gov.uk/'
)
LOGIN_REDIRECT_URL = os.getenv(
    'LOGIN_REDIRECT_URL', DEFAULT_REDIRECT_URL
)
LOGOUT_REDIRECT_URL = os.getenv(
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
ACCOUNT_EMAIL_SUBJECT_PREFIX = os.getenv(
    "ACCOUNT_EMAIL_SUBJECT_PREFIX", 'Your great.gov.uk account: '
)
ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.getenv(
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL", 'https'
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
EMAIL_BACKED_CLASS_NAME = os.getenv('EMAIL_BACKEND_CLASS_NAME', 'default')
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]

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

SESSION_COOKIE_DOMAIN = os.environ['SESSION_COOKIE_DOMAIN']
# env var not same as setting to be more explicit (directory-ui uses same name)
SESSION_COOKIE_NAME = os.environ['SSO_SESSION_COOKIE']
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE') != 'false'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE') != 'false'

# Set with comma separated values in env
ALLOWED_REDIRECT_DOMAINS = os.environ['ALLOWED_REDIRECT_DOMAINS'].split(',')
for domain in ALLOWED_REDIRECT_DOMAINS:
    assert is_valid_domain(domain) is True

# Signature check
SIGNATURE_SECRET = os.environ['SIGNATURE_SECRET']

URLS_EXCLUDED_FROM_SIGNATURE_CHECK = (
    '/api/v1/',
)

# Use proxy host name when generating links (e.g. in emails)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Google tag manager
UTM_COOKIE_DOMAIN = os.environ['UTM_COOKIE_DOMAIN']

# sso profile
SSO_PROFILE_URL = os.environ['SSO_PROFILE_URL']

HEADER_FOOTER_CONTACT_US_URL = os.getenv(
    'HEADER_FOOTER_CONTACT_US_URL',
    'https://contact-us.export.great.gov.uk/directory',
)

FEEDBACK_FORM_URL = os.getenv(
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
DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME = os.getenv(
    'DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME', 'default'
)
DIRECTORY_API_EXTERNAL_CLIENT_CLASS = DIRECTORY_API_EXTERNAL_CLIENT_CLASSES[
    DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME
]
DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET = os.environ[
    'DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET'
]
DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL = os.environ[
    'DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL'
]

# Export Opportunities
EXOPS_APPLICATION_CLIENT_ID = os.environ['EXOPS_APPLICATION_CLIENT_ID']
