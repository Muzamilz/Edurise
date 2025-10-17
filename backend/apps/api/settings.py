"""
API app settings and configuration.
"""

# API Version
API_VERSION = '1.0.0'

# Pagination settings
API_DEFAULT_PAGE_SIZE = 20
API_MAX_PAGE_SIZE = 100

# Rate limiting settings (requests per minute per IP)
API_RATE_LIMIT_PER_MINUTE = 100

# CORS settings for production
API_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Frontend development server
    'http://localhost:5173',  # Vite development server
    # Add production domains here
]

# API Response settings
API_INCLUDE_TIMESTAMP = True
API_INCLUDE_REQUEST_ID = False  # Set to True if you want to track requests

# Logging settings
API_LOG_REQUESTS = True
API_LOG_RESPONSES = True
API_LOG_SLOW_QUERIES = True
API_SLOW_QUERY_THRESHOLD = 1.0  # seconds

# Cache settings
API_CACHE_TIMEOUT = 300  # 5 minutes default
API_CACHE_KEY_PREFIX = 'edurise_api'

# File upload settings
API_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
API_ALLOWED_FILE_TYPES = [
    'image/jpeg', 'image/png', 'image/gif',
    'application/pdf', 'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

# Dashboard settings
DASHBOARD_CACHE_TIMEOUT = 300  # 5 minutes
DASHBOARD_MAX_RECENT_ITEMS = 10
DASHBOARD_TREND_DAYS = 30

# Analytics settings
ANALYTICS_RETENTION_DAYS = 365
ANALYTICS_BATCH_SIZE = 1000

# Error handling settings
API_INCLUDE_STACK_TRACE_IN_DEBUG = True
API_ERROR_TRACKING_ENABLED = True

# Feature flags
FEATURES = {
    'BULK_OPERATIONS': True,
    'ADVANCED_ANALYTICS': True,
    'EXPORT_FUNCTIONALITY': True,
    'REAL_TIME_NOTIFICATIONS': True,
    'AI_RECOMMENDATIONS': True,
}

# External service timeouts
EXTERNAL_SERVICE_TIMEOUT = 30  # seconds
ZOOM_API_TIMEOUT = 15
PAYMENT_API_TIMEOUT = 30
EMAIL_SERVICE_TIMEOUT = 10

# Health check settings
HEALTH_CHECK_CACHE_TIMEOUT = 60  # 1 minute
HEALTH_CHECK_DATABASE_TIMEOUT = 5  # seconds