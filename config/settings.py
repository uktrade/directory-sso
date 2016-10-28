import os

import dj_database_url

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
    'corsheaders',
    'sso.oauth2',
    'sso.user',
]

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# API key shared with clients
API_SECRET = os.environ["API_SECRET"]

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

# Authentication
AUTH_USER_MODEL = 'user.User'
AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
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
LOGIN_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
# HTTP POST is more appropriate, but would require JS in the email
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_SUBJECT_PREFIX = os.getenv(
    "ACCOUNT_EMAIL_SUBJECT_PREFIX", 'Exporting is GREAT Account: '
)
ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.getenv(
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL", 'https'
)
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # seconds
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

# Email
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

LOGOUT_REDIRECT_URL = os.environ['LOGOUT_REDIRECT_URL']

ACCOUNT_ADAPTER = 'sso.adapters.AccountAdapter'
