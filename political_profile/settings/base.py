from pathlib import Path

from celery.schedules import crontab
from decouple import config, Csv
from dj_database_url import parse as dburl

########################################################################
# Basic configuration

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

########################################################################
# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'test_without_migrations',
]

LOCAL_APPS = [
    'political_profile.core.apps.CoreConfig',
    'political_profile.api.apps.ApiConfig',
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'political_profile.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'political_profile.wsgi.application'

########################################################################
# Database

default_dburl = 'sqlite:///' + str(BASE_DIR.joinpath(BASE_DIR, 'db.sqlite3'))

DATABASES = {
    'default': config('DATABASE_URL', default=default_dburl, cast=dburl),
}

########################################################################
# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

########################################################################
# Internationalization

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

########################################################################
# Celery config

CELERY_IMPORTS = 'political_profile.core.tasks',

CELERY_CREATE_MISSING_QUEUES = True

CELERY_TIMEZONE = TIME_ZONE
CELERYBEAT_SYNC_EVERY = True

CELERYBEAT_SCHEDULE = {
    'sample_task': {
        'task': 'political_profile.core.tasks.sample_task',
        'schedule': crontab(),
    }
}

BROKER_URL = config('BROKER_URL', default='amqp://guest@localhost//')

########################################################################
# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR.joinpath('staticfiles'))

########################################################################
# API configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}
