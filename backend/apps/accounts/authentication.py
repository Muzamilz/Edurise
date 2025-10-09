from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth import get_user_model
from .models import Organization

User = get_user_model()


class TenantAwareJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that handles tenant information
    """

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        Also sets tenant information on the request if available.
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(**{'id': user_id})
        except User.DoesNotExist:
            raise InvalidToken('User not found')

        if not user.is_active:
            raise InvalidToken('User is inactive')

        return user

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication. Otherwise returns `None`.
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # Set tenant information on request if available in token
        if 'tenant_id' in validated_token:
            try:
                tenant = Organization.objects.get(
                    id=validated_token['tenant_id'],
                    is_active=True
                )
                request.tenant = tenant
            except Organization.DoesNotExist:
                pass

        return user, validated_token