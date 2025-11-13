from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import User, RevokedToken
from .utils import decode_jwt

class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise exceptions.NotAuthenticated("Authentication credentials were not provided")

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                raise exceptions.NotAuthenticated("Invalid token prefix")
        except ValueError:
            raise exceptions.NotAuthenticated("Invalid Authorization header format")

        if RevokedToken.objects.filter(token=token).exists():
            raise exceptions.AuthenticationFailed("Token has been revoked")

        payload = decode_jwt(token)
        if not payload:
            raise exceptions.AuthenticationFailed("Invalid or expired token")

        try:
            user = User.objects.get(id=payload["user_id"], is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found or inactive")

        return (user, None)

    def authenticate_header(self, request):
        """
        DRF uses this to return the WWW-Authenticate header.
        This ensures a 401 response instead of 403 for unauthenticated requests.
        """
        return 'Bearer realm="api"'
