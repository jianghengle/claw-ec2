import os
from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
