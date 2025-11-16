"""
Django settings for LibraryProject project.
Enhanced Security Configuration for HTTPS and Secure Headers
"""

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Security: Allowed hosts for production - Update with your actual domain
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '.yourdomain.com',  # Replace with your actual domain
    '.yourapp.herokuapp.com',  # If deploying to Heroku
    '.railway.app',  # If deploying to Railway
]

# Security: Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party security apps
    'csp',  # Content Security Policy
    # Local apps
    'bookshelf',
    'relationship_app',
]

# Security: Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
    'csp.middleware.CSPMiddleware',  # Content Security Policy
]

ROOT_URLCONF = 'LibraryProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'LibraryProject.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Security: Minimum password length
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'relationship_app.CustomUser'

# ==================== HTTPS & SECURITY CONFIGURATIONS ====================

# Security: HTTPS Settings (for production)
# These settings are automatically disabled when DEBUG=True
SECURE_SSL_REDIRECT = not DEBUG  # Redirect HTTP to HTTPS in production
SECURE_HSTS_SECONDS = 31536000  # 1 year - Force HTTPS for this duration
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply HSTS to all subdomains
SECURE_HSTS_PRELOAD = True  # Allow preloading in HSTS preload lists

# Security: Browser Protection Headers
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filter in browsers
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking - DENY any framing
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing

# Security: Session settings with HTTPS enforcement
SESSION_COOKIE_SECURE = not DEBUG  # Send session cookie over HTTPS only
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser closes

# Security: CSRF settings with HTTPS enforcement
CSRF_COOKIE_SECURE = not DEBUG  # Send CSRF cookie over HTTPS only
CSRF_COOKIE_HTTPONLY = True  # Make CSRF cookie HTTPOnly
CSRF_USE_SESSIONS = True  # Store CSRF token in session instead of cookie

# Security: Content Security Policy (CSP) Configuration
CONTENT_SECURITY_POLICY = {
    'DEFAULT_SRC': ["'self'"],
    'SCRIPT_SRC': ["'self'"],
    'STYLE_SRC': ["'self'", "'unsafe-inline'"],  # Allow inline styles for Django admin
    'IMG_SRC': ["'self'", "data:"],
    'FONT_SRC': ["'self'"],
    'OBJECT_SRC': ["'none'"],
    'BASE_URI': ["'self'"],
    'FORM_ACTION': ["'self'"],
    'FRAME_ANCESTORS': ["'none'"],  # Equivalent to X-Frame-Options: DENY
}

# Security: Additional headers
SECURE_REFERRER_POLICY = 'same-origin'  # Limit referrer information

# Security: File upload restrictions
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB max file upload
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880   # 5MB max data upload

# Security: Email backend (for production)
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # Configure these in your production environment
    # EMAIL_HOST = 'smtp.your-email-provider.com'
    # EMAIL_PORT = 587
    # EMAIL_USE_TLS = True
    # EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    # EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security: Logging configuration for security events
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['security_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Security: Additional production settings
if not DEBUG:
    # Ensure proper content type handling
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')