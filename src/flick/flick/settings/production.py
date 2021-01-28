"""
Django settings for flick project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "celery",
    "django_celery_results",
    "friendship",
    "rest_framework",
    "rest_framework.authtoken",
    "push_notifications",
    "asset",
    "api",
    "comment",
    "friend",
    "lst",
    "like",
    "notification",
    "provider",
    "rating",
    "read",
    "search",
    "show",
    "suggestion",
    "tag",
    "user",
]

PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": config("FCM_API_KEY"),
    "APNS_CERTIFICATE": config("APNS_CERTIFICATE"),
    "APNS_TOPIC": config("APPLE_BUNDLE_ID"),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "flick.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# needed to test in Postman
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"]}

WSGI_APPLICATION = "flick.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("POSTGRES_NAME"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/static"

S3_BUCKET = "flick"
S3_BASE_URL = f"https://{S3_BUCKET}.s3-us-west-1.amazonaws.com/"

# Celery config
CELERY_BROKER_URL = "pyamqp://rabbitmq:5672"
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Third party APIs
TMDB_API_KEY = config("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_BASE_IMAGE_URL = "http://image.tmdb.org/t/p/w400"
VALIDATE_SOCIAL_TOKEN = False
VALIDATE_FACEBOOK_TOKEN_URL = "https://graph.facebook.com/me"
VALIDATE_FACEBOOK_ID_AND_TOKEN_URL = "https://graph.facebook.com/me?fields=id&access_token="
APPLE_KEY_ID = config("APPLE_KEY_ID")
APPLE_TEAM_ID = config("APPLE_TEAM_ID")
APPLE_BUNDLE_ID = config("APPLE_BUNDLE_ID")
APPLE_PRIVATE_KEY = config("APPLE_PRIVATE_KEY")
VALIDATE_APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"

# Testing
# TEST_RUNNER = "django_slowtests.testrunner.DiscoverSlowestTestsRunner"
# NUM_SLOW_TESTS = 5

# Caches
CACHES = {
    "default": {
        "BACKEND": "lrucache_backend.LRUObjectCache",
        "TIMEOUT": 600,
        "OPTIONS": {"MAX_ENTRIES": 100, "CULL_FREQUENCY": 100},
        "NAME": "optional-name",
    },
    "local": {
        "BACKEND": "lrucache_backend.LRUObjectCache",
        "TIMEOUT": 600,
        "OPTIONS": {"MAX_ENTRIES": 100, "CULL_FREQUENCY": 100},
        "NAME": "optional-name",
    },
}

# read in the APPLE_PRIVATE_KEY
with open("apple_private.p8", mode="rb") as key_file:
    APPLE_PRIVATE_KEY = key_file.read()
