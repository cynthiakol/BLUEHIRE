from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#(tk@fosbc4^gi(5-(6hr=hh6@=muh^dznz$(#i61m3x0-ko1x'

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'your-static-domain.ngrok-free.app']
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
SITE_URL = "https://your-static-domain.ngrok-free.app"

# ============================================================
# NGROK/HTTPS CONFIGURATION
# ============================================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # oauth apps
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    # your apps
    'accounts',
    'jobs',
    'core',
    'applications',
    'systemlogs',
    'ratings',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'bluehire.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "core", "static")]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bluehire',
        'USER': 'bluehire',
        'PASSWORD': '42069',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': (
                "SET sql_mode='STRICT_TRANS_TABLES';"
                "SET innodb_strict_mode=1;"
                "SET SESSION innodb_default_row_format='dynamic';"
            ),
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LOGIN_URL = '/accounts/signin_register/'
AUTH_USER_MODEL = 'accounts.Users'
SILENCED_SYSTEM_CHECKS = ['models.W042']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SITE_URL = "http://127.0.0.1:8000"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "augustine.comon@gmail.com"
EMAIL_HOST_PASSWORD = "intc ndsx enst tewe"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LOGOUT_REDIRECT_URL = '/accounts/signin_register/'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ============================================================
# OAUTH & ALLAUTH CONFIGURATION
# ============================================================

SITE_ID = 1

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'   # ← CHANGED from 'https' to 'http'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_ADAPTER = 'accounts.adapters.MySocialAccountAdapter'

SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = False

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = True

SOCIALACCOUNT_EMAIL_AUTHENTICATION = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

LOGIN_REDIRECT_URL = '/select-role/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/signin_register/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/accounts/signin_register/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['public_profile'],
        'AUTH_PARAMS': {
            'auth_type': 'rerequest',
        },
        'FIELDS': [
            'id', 'name', 'first_name', 'last_name',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v18.0',
    }
}

SOCIALACCOUNT_LOGIN_ON_GET = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'