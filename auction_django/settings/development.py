from .base import *

DEBUG = True

DATABASES = {'default': dj_database_url.config()}
DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = '1025'
