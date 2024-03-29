"""
Django settings for standards_lab project.

Generated by 'django-admin startproject' using Django 2.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ
import warnings

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from django.utils.crypto import get_random_string


chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)"
secret_key = get_random_string(50, chars)
if "SECRET_KEY" not in os.environ:
    warnings.warn(
        "SECRET_KEY should be added to Environment Variables. Random key will be used instead."
    )


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env(
    REDIS_URL=(str, "redis://localhost:6379"),
    ROOT_PROJECTS_DIR=(str, "/tmp/standards-lab/"),
    ALLOWED_HOSTS=(list, []),
    DEBUG=(bool, True),
    SECRET_KEY=(str, secret_key),
    STATIC_ROOT=(str, os.path.join(BASE_DIR, "staticfiles")),
    SENTRY_DSN=(str, None),
)

# SECURITY WARNING: keep the secret key used in production secret!
SENTRY_DSN = env("SENTRY_DSN")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=False,
        # By default the SDK will try to use the SENTRY_RELEASE
        # environment variable, or infer a git commit
        # SHA as release, however you may want to set
        # something more human-readable.
        # release="myapp@1.0.0",
    )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    # Our apps:
    "api",
    "ui",
    "processor",
    # 3d party:
    "django_rq",
    "cove",
    # Django stuff:
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "ui.context_processor.common",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = env("STATIC_ROOT")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

INTERNAL_IPS = ("127.0.0.1",)

REDIS_URL = env("REDIS_URL")

# Redis Session backend
# https://github.com/martinrusev/django-redis-sessions

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# RQ redis connection settings
# https://github.com/rq/django-rq/blob/master/README.rst

RQ_QUEUES = {
    "default": {"URL": f"{REDIS_URL}/0"},
}

EDIT_MODE = True

ROOT_PROJECTS_DIR = env("ROOT_PROJECTS_DIR")

# MIME types of files allowed in project
ALLOWED_PROJECT_MIME_TYPES = [
    "application/json",
    "application/csv",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.oasis.opendocument.spreadsheet",
]
