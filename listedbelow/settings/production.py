"""
Production settings.
"""
from decouple import config
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='listedbelow.com,www.listedbelow.com').split(',')

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
