from django.http import Http404
from apps.accounts.models import Organization


class TenantMiddleware:
    """Middleware to detect and set current tenant based on subdomain"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract subdomain from host
        host = request.get_host().split(':')[0]  # Remove port if present
        subdomain = self.extract_subdomain(host)
        
        # Set tenant on request
        request.tenant = None
        if subdomain:
            try:
                request.tenant = Organization.objects.get(
                    subdomain=subdomain,
                    is_active=True
                )
            except Organization.DoesNotExist:
                # For API endpoints, we might want to allow requests without tenant
                # For tenant-specific pages, you might want to raise Http404
                pass
        
        response = self.get_response(request)
        return response
    
    def extract_subdomain(self, host):
        """Extract subdomain from host"""
        # Skip localhost and IP addresses
        if host in ['localhost', '127.0.0.1'] or host.replace('.', '').isdigit():
            return None
        
        parts = host.split('.')
        if len(parts) > 2:
            return parts[0]  # Return first part as subdomain
        
        return None