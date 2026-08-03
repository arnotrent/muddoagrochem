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

# ─────────────────────────────────────────────────────────────────
# MEDIA STORAGE
#
# By default, uploaded files (product photos, chat attachments, staff
# avatars) go to local disk under MEDIA_ROOT. That works fine in dev,
# but on Render's free plan the filesystem is EPHEMERAL — uploads
# vanish the next time the service restarts or redeploys, even though
# the URL routing to serve them (below, in urls.py) is correct.
#
# If AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_STORAGE_BUCKET_NAME
# are set (e.g. as Render environment variables), media automatically
# switches to S3-backed storage instead, which survives restarts.
# Without them, it falls back to local disk exactly as before — nothing
# breaks if you don't set these up, but attachments/photos will keep
# disappearing on Render's free tier until you do.
# ─────────────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME    = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN  = os.environ.get('AWS_S3_CUSTOM_DOMAIN', '')  # optional CDN/custom domain

USE_S3_MEDIA = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME)

if USE_S3_MEDIA:
    INSTALLED_APPS.append('storages')
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    else:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/'
    MEDIA_ROOT = BASE_DIR / 'media'  # unused when S3 is active, kept for completeness
else:
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
COMPANY_EMAIL     = 'muddoagro811@gmail.com'
COMPANY_ADDRESS   = 'Container Village Nakivubo, Equity Bank Basement V013, Kampala'
