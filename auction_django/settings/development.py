from .base import *

DEBUG = True

DATABASES = {'default': dj_database_url.config()}
DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
