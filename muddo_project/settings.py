import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'muddo-dev-CHANGE-IN-PROD-xk92abc2024!@#')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://*.fly.dev',
    'https://*.herokuapp.com',
    'http://localhost:8000',
    'http://localhost:3000',
    'http://127.0.0.1:8000',
]
_render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
if _render_url and _render_url not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(_render_url)
_custom_domain = os.environ.get('CUSTOM_DOMAIN', '')
if _custom_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_custom_domain}')
    CSRF_TRUSTED_ORIGINS.append(f'http://{_custom_domain}')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth',
    'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles',
    'apps.core', 'apps.products', 'apps.inventory', 'apps.agents',
    'apps.requests_app', 'apps.messaging', 'apps.distributors', 'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'muddo_project.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'apps.core.context_processors.global_context',
    ]}}]

WSGI_APPLICATION = 'muddo_project.wsgi.application'

DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'muddo.db',
}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/admin-panel/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_AGE = 86400 * 7

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('MAIL_USERNAME', 'muddoagro811@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'Muddo Agro Chemicals <muddoagro811@gmail.com>'
if not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

GA_MEASUREMENT_ID = os.environ.get('GA_MEASUREMENT_ID', '')
WHATSAPP_NUMBER   = os.environ.get('WHATSAPP_NUMBER', '256772507582')
GOOGLE_MAPS_KEY   = os.environ.get('GOOGLE_MAPS_KEY', '')
COMPANY_PHONE     = '+256 772 507582 / 0702-507582'
COMPANY_EMAIL     = 'kulanju_w@yahoo.com'
COMPANY_ADDRESS   = 'Container Village Nakivubo, Equity Bank Basement V013, Kampala'
