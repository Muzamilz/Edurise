from django.http import Http404, JsonResponse
from django.utils import timezone
from apps.accounts.models import Organization
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """Middleware to detect and set current tenant based on subdomain or header"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract tenant from subdomain or header
        tenant = self.get_tenant_from_request(request)
        
        # Set tenant on request
        request.tenant = tenant
        
        # Add tenant context to response
        response = self.get_response(request)
        
        # Add tenant information to API responses
        if request.path.startswith('/api/') and tenant:
            response['X-Tenant-ID'] = str(tenant.id)
            response['X-Tenant-Name'] = tenant.name
            response['X-Tenant-Subdomain'] = tenant.subdomain
        
        return response
    
    def get_tenant_from_request(self, request):
        """Get tenant from request (subdomain or header)"""
        tenant = None
        
        # First, try to get tenant from X-Tenant-ID header (for API requests)
        tenant_id = request.META.get('HTTP_X_TENANT_ID')
        if tenant_id:
            try:
                tenant = Organization.objects.get(id=tenant_id, is_active=True)
                logger.debug(f"Tenant found from header: {tenant.subdomain}")
                return tenant
            except (Organization.DoesNotExist, ValueError):
                logger.warning(f"Invalid tenant ID in header: {tenant_id}")
        
        # Then, try to get tenant from subdomain
        host = request.get_host().split(':')[0]  # Remove port if present
        subdomain = self.extract_subdomain(host)
        
        if subdomain:
            try:
                tenant = Organization.objects.get(
                    subdomain=subdomain,
                    is_active=True
                )
                logger.debug(f"Tenant found from subdomain: {tenant.subdomain}")
            except Organization.DoesNotExist:
                logger.warning(f"Tenant not found for subdomain: {subdomain}")
                # For API endpoints, we might want to allow requests without tenant
                # For tenant-specific pages, you might want to raise Http404
                if not request.path.startswith('/api/'):
                    # For non-API requests, you might want to redirect to main site
                    pass
        
        return tenant
    
    def extract_subdomain(self, host):
        """Extract subdomain from host"""
        # Skip localhost and IP addresses
        if host in ['localhost', '127.0.0.1'] or host.replace('.', '').isdigit():
            return None
        
        # Skip common non-tenant subdomains
        skip_subdomains = ['www', 'api', 'admin', 'mail', 'ftp', 'cdn', 'static']
        
        parts = host.split('.')
        if len(parts) > 2:
            subdomain = parts[0]
            if subdomain not in skip_subdomains:
                return subdomain
        
        return None


class TenantBrandingMiddleware:
    """Middleware to add tenant-specific branding context"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add tenant branding to API responses
        if request.path.startswith('/api/') and hasattr(request, 'tenant') and request.tenant:
            tenant = request.tenant
            
            # Add branding headers
            if tenant.primary_color:
                response['X-Tenant-Primary-Color'] = tenant.primary_color
            if tenant.secondary_color:
                response['X-Tenant-Secondary-Color'] = tenant.secondary_color
            if tenant.logo:
                response['X-Tenant-Logo-URL'] = request.build_absolute_uri(tenant.logo.url)
        
        return response


class TenantAccessControlMiddleware:
    """Middleware to enforce tenant-based access control"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip access control for certain paths
        skip_paths = [
            '/api/health/',
            '/api/v1/accounts/auth/',
            '/api/v1/organizations/by_subdomain/',
            '/admin/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # For API requests, ensure user has access to the tenant
        if (request.path.startswith('/api/') and 
            hasattr(request, 'user') and 
            request.user.is_authenticated and 
            hasattr(request, 'tenant') and 
            request.tenant):
            
            # Check if user has access to this tenant
            from apps.accounts.models import UserProfile
            
            if not UserProfile.objects.filter(
                user=request.user, 
                tenant=request.tenant
            ).exists() and not request.user.is_superuser:
                
                return JsonResponse({
                    'success': False,
                    'message': 'Access denied to this organization',
                    'error_code': 'TENANT_ACCESS_DENIED',
                    'timestamp': timezone.now().isoformat()
                }, status=403)
        
        return self.get_response(request)