import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = BASE_DIR / '.env.development'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  Environment file not found: {env_file}")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'channels',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

LOCAL_APPS = [
    'apps.api',  # Centralized API app
    'apps.accounts',
    'apps.courses',
    'apps.classes',
    'apps.assignments',
    'apps.payments',
    'apps.ai',
    'apps.notifications',
    'apps.admin_tools',
    'apps.files',  # File management app
    'apps.security',  # Security and compliance app
    'apps.common',
    'apps.content',  # Content management app
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'apps.security.middleware.SecurityHeadersMiddleware',  # Security headers
    'apps.security.middleware.RateLimitingMiddleware',  # Rate limiting
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.security.middleware.CSRFEnhancementMiddleware',  # Enhanced CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middleware.TenantMiddleware',  # Custom tenant middleware
    'apps.security.middleware.InputValidationMiddleware',  # Input validation
    'apps.security.middleware.SecurityMonitoringMiddleware',  # Security monitoring
    'apps.security.middleware.AuditLoggingMiddleware',  # Audit logging
    'apps.api.middleware.APILoggingMiddleware',  # API request/response logging
    'apps.api.middleware.APIVersioningMiddleware',  # API versioning
    'apps.api.middleware.APIErrorHandlingMiddleware',  # Standardized error handling
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'edurise_lms'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.accounts.authentication.TenantAwareJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.api.responses.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'apps.api.exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@edurise.com')

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

# Third-party API Keys
# Zoom Configuration
ZOOM_ACCOUNT_ID = os.environ.get('ZOOM_ACCOUNT_ID', os.environ.get('ZOOM_API_KEY', ''))
ZOOM_CLIENT_ID = os.environ.get('ZOOM_CLIENT_ID', os.environ.get('ZOOM_API_KEY', ''))
ZOOM_CLIENT_SECRET = os.environ.get('ZOOM_CLIENT_SECRET', os.environ.get('ZOOM_API_SECRET', ''))
ZOOM_BASE_URL = os.environ.get('ZOOM_BASE_URL', 'https://api.zoom.us/v2')
ZOOM_WEBHOOK_SECRET = os.environ.get('ZOOM_WEBHOOK_SECRET', '')

# Legacy Zoom settings (for backward compatibility)
ZOOM_API_KEY = os.environ.get('ZOOM_API_KEY', '')
ZOOM_API_SECRET = os.environ.get('ZOOM_API_SECRET', '')

# Payment Gateway Configuration
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# PayPal Configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
PAYPAL_BASE_URL = os.environ.get('PAYPAL_BASE_URL', 'https://api.sandbox.paypal.com')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')

# Payment Settings
DEFAULT_CURRENCY = os.environ.get('DEFAULT_CURRENCY', 'USD')
PAYMENT_SUCCESS_URL = os.environ.get('PAYMENT_SUCCESS_URL', 'http://localhost:3000/payment/success')
PAYMENT_CANCEL_URL = os.environ.get('PAYMENT_CANCEL_URL', 'http://localhost:3000/payment/cancel')

# Admin Configuration
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@edurise.com')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# AI Configuration
AI_CACHE_TIMEOUT = os.environ.get('AI_CACHE_TIMEOUT', 3600)  # 1 hour default
AI_MAX_RETRIES = os.environ.get('AI_MAX_RETRIES', 3)
AI_RESPONSE_QUALITY_THRESHOLD = os.environ.get('AI_RESPONSE_QUALITY_THRESHOLD', 0.8)

# Frontend URL for email links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session Security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True
CSRF_FAILURE_VIEW = 'apps.security.views.csrf_failure'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://apis.google.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'", "https://api.zoom.us", "https://generativelanguage.googleapis.com")

# File Upload Security
ALLOWED_FILE_EXTENSIONS = [
    # Documents
    'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
    # Images
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',
    # Videos
    'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm',
    # Audio
    'mp3', 'wav', 'ogg', 'aac', 'm4a',
    # Archives
    'zip', 'rar', '7z', 'tar', 'gz',
    # Presentations
    'ppt', 'pptx', 'odp',
    # Spreadsheets
    'xls', 'xlsx', 'ods', 'csv'
]

BLOCKED_FILE_EXTENSIONS = [
    'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
    'php', 'asp', 'aspx', 'jsp', 'py', 'pl', 'sh', 'ps1'
]

MAX_FILE_SIZE_MB = 100  # 100MB max file size
VIRUS_SCAN_ENABLED = True
FILE_QUARANTINE_ENABLED = True

# Rate Limiting
RATE_LIMIT_ENABLE = True
RATE_LIMIT_PER_MINUTE = 100
RATE_LIMIT_PER_HOUR = 1000
RATE_LIMIT_PER_DAY = 10000

# Security Monitoring
SECURITY_MONITORING_ENABLED = True
FAILED_LOGIN_THRESHOLD = 5
ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes
SUSPICIOUS_ACTIVITY_THRESHOLD = 10
INTRUSION_DETECTION_ENABLED = True

# Audit Logging
AUDIT_LOG_ENABLED = True
AUDIT_LOG_RETENTION_DAYS = 365
AUDIT_LOG_SENSITIVE_FIELDS = ['password', 'token', 'secret', 'key']

# GDPR Compliance
GDPR_COMPLIANCE_ENABLED = True
DATA_RETENTION_DAYS = 365
AUTO_DELETE_INACTIVE_USERS_DAYS = 730  # 2 years
CONSENT_TRACKING_ENABLED = True

# Encryption Settings
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', SECRET_KEY)
ENCRYPT_SENSITIVE_DATA = True

# Django Sites Framework
SITE_ID = 1

# Django Allauth Configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Updated allauth settings (new format)
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'

# Social Account Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Google OAuth Settings
GOOGLE_OAUTH2_CLIENT_ID = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID', '')
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET', '')

# dj-rest-auth Configuration
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'jwt-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'jwt-refresh-token',
    'JWT_AUTH_HTTPONLY': False,
}

# Email confirmation URLs
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = f'{FRONTEND_URL}/email-confirmed/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = f'{FRONTEND_URL}/email-confirmed/'

# API Configuration
API_VERSION = '1.0.0'
API_DEFAULT_PAGE_SIZE = 20
API_MAX_PAGE_SIZE = 100
API_RATE_LIMIT_PER_MINUTE = 100

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Frontend development
    'http://localhost:5173',  # Vite development
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-tenant-id',  # Allow our custom tenant header
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# API CORS settings (legacy - keeping for compatibility)
API_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Frontend development
    'http://localhost:5173',  # Vite development
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

# API Response settings
API_INCLUDE_TIMESTAMP = True
API_INCLUDE_REQUEST_ID = False

# Dashboard settings
DASHBOARD_CACHE_TIMEOUT = 300  # 5 minutes
DASHBOARD_MAX_RECENT_ITEMS = 10
DASHBOARD_TREND_DAYS = 30

# Suppress third-party deprecation warnings
import warnings
warnings.filterwarnings('ignore', message='app_settings.USERNAME_REQUIRED is deprecated')
warnings.filterwarnings('ignore', message='app_settings.EMAIL_REQUIRED is deprecated')

# Logging configuration for API
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'api.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'apps.api': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}