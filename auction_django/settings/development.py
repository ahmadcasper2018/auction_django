from .base import *

DEBUG = True

DATABASES = {'default': dj_database_url.config()}
DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

THIRD_PART_APPS = THIRD_PART_APPS + [
    'django_extensions',
]

DEFAULT_FROM_EMAIL = "mofa_user@gmail.com"
EMAIL_HOST = "mailhog"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False