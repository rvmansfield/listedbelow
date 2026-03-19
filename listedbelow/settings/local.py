"""
Local development settings.
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['*']

# Use console email backend for development (override .env)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
