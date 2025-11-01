from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from .responses import StandardAPIResponse
import sys
import django


class APIHealthCheckView(APIView):
    """
    API health check endpoint to verify system status.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return system health status including database, cache, and basic metrics.
        """
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': getattr(settings, 'API_VERSION', '1.0.0'),
            'django_version': django.get_version(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'checks': {}
        }
        
        # Database health check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_data['checks']['database'] = {
                    'status': 'healthy',
                    'response_time_ms': 0  # Could measure actual response time
                }
        except Exception as e:
            health_data['status'] = 'unhealthy'
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Cache health check
        try:
            cache_key = 'health_check_test'
            cache.set(cache_key, 'test_value', 30)
            cached_value = cache.get(cache_key)
            if cached_value == 'test_value':
                health_data['checks']['cache'] = {'status': 'healthy'}
            else:
                health_data['checks']['cache'] = {'status': 'unhealthy', 'error': 'Cache read/write failed'}
        except Exception as e:
            health_data['status'] = 'unhealthy'
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Add basic system metrics
        health_data['metrics'] = {
            'uptime_seconds': (timezone.now() - timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds(),
            'debug_mode': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS if not settings.DEBUG else ['*']
        }
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return StandardAPIResponse.success(
            data=health_data,
            message=f"API is {health_data['status']}",
            status_code=status_code
        )


class APIDocumentationView(APIView):
    """
    API documentation endpoint providing information about available endpoints.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return comprehensive API documentation for frontend integration.
        """
        base_url = request.build_absolute_uri('/api/v1/')
        
        documentation = {
            'api_version': getattr(settings, 'API_VERSION', '1.0.0'),
            'base_url': base_url,
            'authentication': {
                'type': 'JWT Bearer Token',
                'header': 'Authorization: Bearer <token>',
                'login_endpoint': f'{base_url}accounts/auth/login/',
                'refresh_endpoint': f'{base_url}accounts/auth/refresh/',
                'logout_endpoint': f'{base_url}accounts/auth/logout/',
                'register_endpoint': f'{base_url}accounts/auth/register/',
            },
            'tenant_header': {
                'description': 'Multi-tenant support via header',
                'header': 'X-Tenant: <subdomain>',
                'required': 'For most endpoints except authentication'
            },
            'response_format': {
                'success_example': {
                    'success': True,
                    'data': {'example': 'data'},
                    'message': 'Operation completed successfully',
                    'timestamp': '2024-01-01T00:00:00Z',
                    'meta': {'pagination': {'page': 1, 'total_pages': 5}}
                },
                'error_example': {
                    'success': False,
                    'message': 'Error description',
                    'errors': {'field': ['Field error message']},
                    'error_code': 'VALIDATION_ERROR',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            },
            'core_endpoints': {
                'health_check': f'{request.build_absolute_uri("/api/health/")}',
                'api_documentation': f'{request.build_absolute_uri("/api/docs/")}',
            },
            'dashboard_endpoints': {
                'student_dashboard': f'{base_url}dashboard/student/',
                'teacher_dashboard': f'{base_url}dashboard/teacher/',
                'admin_dashboard': f'{base_url}dashboard/admin/',
                'superadmin_dashboard': f'{base_url}dashboard/superadmin/',
            },
            'resource_endpoints': {
                'users': {
                    'list_create': f'{base_url}users/',
                    'detail': f'{base_url}users/{{id}}/',
                    'description': 'User management',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'organizations': {
                    'list_create': f'{base_url}organizations/',
                    'detail': f'{base_url}organizations/{{id}}/',
                    'description': 'Organization/tenant management',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'course_categories': {
                    'list_create': f'{base_url}course-categories/',
                    'detail': f'{base_url}course-categories/{{id}}/',
                    'root_categories': f'{base_url}course-categories/root_categories/',
                    'hierarchy': f'{base_url}course-categories/hierarchy/',
                    'subcategories': f'{base_url}course-categories/{{id}}/subcategories/',
                    'description': 'Course category management with hierarchy support',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'courses': {
                    'list_create': f'{base_url}courses/',
                    'detail': f'{base_url}courses/{{id}}/',
                    'marketplace': f'{base_url}courses/marketplace_enhanced/',
                    'recommendations': f'{base_url}courses/recommendations/',
                    'dashboard_stats': f'{base_url}courses/dashboard_stats/',
                    'analytics': f'{base_url}courses/{{id}}/analytics/',
                    'enroll': f'{base_url}courses/{{id}}/enroll/',
                    'students': f'{base_url}courses/{{id}}/students/',
                    'description': 'Course management and enrollment',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'enrollments': {
                    'list_create': f'{base_url}enrollments/',
                    'detail': f'{base_url}enrollments/{{id}}/',
                    'dashboard': f'{base_url}enrollments/dashboard/',
                    'update_progress': f'{base_url}enrollments/{{id}}/update_progress/',
                    'description': 'Student enrollment management',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'live_classes': {
                    'list_create': f'{base_url}live-classes/',
                    'detail': f'{base_url}live-classes/{{id}}/',
                    'upcoming': f'{base_url}live-classes/upcoming/',
                    'join_info': f'{base_url}live-classes/{{id}}/join_info/',
                    'start_class': f'{base_url}live-classes/{{id}}/start_class/',
                    'end_class': f'{base_url}live-classes/{{id}}/end_class/',
                    'description': 'Live class management with Zoom integration',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'payments': {
                    'list_create': f'{base_url}payments/',
                    'detail': f'{base_url}payments/{{id}}/',
                    'subscriptions': f'{base_url}subscriptions/',
                    'invoices': f'{base_url}invoices/',
                    'description': 'Payment processing and billing',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'notifications': {
                    'list_create': f'{base_url}notifications/',
                    'detail': f'{base_url}notifications/{{id}}/',
                    'mark_read': f'{base_url}notifications/{{id}}/mark_read/',
                    'description': 'User notifications',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'ai_features': {
                    'conversations': f'{base_url}ai-conversations/',
                    'content_summaries': f'{base_url}ai-content-summaries/',
                    'quizzes': f'{base_url}ai-quizzes/',
                    'usage_stats': f'{base_url}ai-usage/',
                    'description': 'AI-powered features and analytics',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'assignments': {
                    'list_create': f'{base_url}assignments/',
                    'detail': f'{base_url}assignments/{{id}}/',
                    'publish': f'{base_url}assignments/{{id}}/publish/',
                    'close': f'{base_url}assignments/{{id}}/close/',
                    'statistics': f'{base_url}assignments/{{id}}/statistics/',
                    'bulk_grade': f'{base_url}assignments/{{id}}/bulk_grade/',
                    'upcoming': f'{base_url}assignments/upcoming/',
                    'overdue': f'{base_url}assignments/overdue/',
                    'description': 'Assignment management and grading',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'submissions': {
                    'list_create': f'{base_url}submissions/',
                    'detail': f'{base_url}submissions/{{id}}/',
                    'submit': f'{base_url}submissions/{{id}}/submit/',
                    'grade': f'{base_url}submissions/{{id}}/grade/',
                    'my_submissions': f'{base_url}submissions/my_submissions/',
                    'pending_grading': f'{base_url}submissions/pending_grading/',
                    'description': 'Student assignment submissions and grading',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'certificates': {
                    'list_create': f'{base_url}certificates/',
                    'detail': f'{base_url}certificates/{{id}}/',
                    'issue': f'{base_url}certificates/{{id}}/issue/',
                    'revoke': f'{base_url}certificates/{{id}}/revoke/',
                    'verify': f'{base_url}certificates/verify/?certificate_number={{number}}',
                    'my_certificates': f'{base_url}certificates/my_certificates/',
                    'description': 'Certificate generation and verification',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'course_progress': {
                    'list_create': f'{base_url}course-progress/',
                    'detail': f'{base_url}course-progress/{{id}}/',
                    'update_progress': f'{base_url}course-progress/{{id}}/update_progress/',
                    'course_analytics': f'{base_url}course-progress/course_analytics/?course_id={{id}}',
                    'student_dashboard': f'{base_url}course-progress/student_dashboard/',
                    'description': 'Course progress tracking and analytics',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                },
                'wishlist': {
                    'list_create': f'{base_url}wishlist/',
                    'detail': f'{base_url}wishlist/{{id}}/',
                    'add_course': f'{base_url}wishlist/add_course/',
                    'remove_course': f'{base_url}wishlist/remove_course/',
                    'analytics': f'{base_url}wishlist/analytics/',
                    'bulk_enroll': f'{base_url}wishlist/bulk_enroll/',
                    'update_notifications': f'{base_url}wishlist/update_notifications/',
                    'description': 'Course wishlist management with analytics and bulk operations',
                    'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
                }
            },
            'authentication_flow': {
                'step_1': 'POST to /api/v1/accounts/auth/login/ with email and password',
                'step_2': 'Include "Authorization: Bearer <access_token>" in subsequent requests',
                'step_3': 'Include "X-Tenant: <subdomain>" header for tenant-specific data',
                'step_4': 'Use refresh token to get new access token when expired'
            },
            'common_query_parameters': {
                'pagination': {
                    'page': 'Page number (default: 1)',
                    'page_size': 'Items per page (default: 20, max: 100)'
                },
                'filtering': {
                    'search': 'Search query across searchable fields',
                    'ordering': 'Sort by field (prefix with - for descending)',
                    'category': 'Filter by category (for courses)',
                    'status': 'Filter by status (for enrollments, payments, etc.)'
                }
            },
            'error_codes': {
                'VALIDATION_ERROR': 'Request data validation failed',
                'PERMISSION_DENIED': 'User lacks required permissions',
                'NOT_FOUND': 'Requested resource not found',
                'UNAUTHORIZED': 'Authentication required',
                'RATE_LIMIT_EXCEEDED': 'Too many requests',
                'SERVER_ERROR': 'Internal server error'
            },
            'frontend_integration_examples': {
                'fetch_courses': {
                    'url': f'{base_url}courses/',
                    'method': 'GET',
                    'headers': {
                        'Authorization': 'Bearer <token>',
                        'X-Tenant': '<subdomain>',
                        'Content-Type': 'application/json'
                    }
                },
                'enroll_in_course': {
                    'url': f'{base_url}courses/{{course_id}}/enroll/',
                    'method': 'POST',
                    'headers': {
                        'Authorization': 'Bearer <token>',
                        'X-Tenant': '<subdomain>',
                        'Content-Type': 'application/json'
                    }
                },
                'get_student_dashboard': {
                    'url': f'{base_url}dashboard/student/',
                    'method': 'GET',
                    'headers': {
                        'Authorization': 'Bearer <token>',
                        'X-Tenant': '<subdomain>'
                    }
                }
            }
        }
        
        return StandardAPIResponse.success(
            data=documentation,
            message="API documentation retrieved successfully"
        )