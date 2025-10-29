"""
ASGI config for edurise project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from apps.notifications.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django_asgi_app = get_asgi_application()

# Enhanced WebSocket middleware for authentication and tenant support
class WebSocketAuthMiddleware:
    """Enhanced WebSocket authentication middleware with tenant support"""
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        # Extract token from query parameters
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        
        token = query_params.get('token')
        tenant_id = query_params.get('tenant')
        
        # Add token and tenant to scope for consumers to use
        scope['auth_token'] = token
        scope['tenant_id'] = tenant_id
        
        # Validate token if provided
        if token:
            try:
                from rest_framework_simplejwt.tokens import UntypedToken
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                from django.contrib.auth import get_user_model
                from django.contrib.auth.models import AnonymousUser
                import jwt
                from django.conf import settings
                
                # Validate JWT token
                UntypedToken(token)
                
                # Decode token to get user
                decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get('user_id')
                
                if user_id:
                    User = get_user_model()
                    try:
                        user = await User.objects.aget(id=user_id)
                        scope['user'] = user
                    except User.DoesNotExist:
                        scope['user'] = AnonymousUser()
                else:
                    scope['user'] = AnonymousUser()
                    
            except (InvalidToken, TokenError, jwt.InvalidTokenError):
                scope['user'] = AnonymousUser()
        
        # Add tenant information to scope
        if tenant_id:
            try:
                from apps.tenants.models import Tenant
                tenant = await Tenant.objects.aget(id=tenant_id)
                scope['tenant'] = tenant
            except:
                scope['tenant'] = None
        
        return await self.inner(scope, receive, send)

def WebSocketAuthMiddlewareStack(inner):
    return WebSocketAuthMiddleware(AuthMiddlewareStack(inner))

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        WebSocketAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})