from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from rest_framework import authentication
from rest_framework import exceptions
from common.apiresponse import ApiResponse
from common.jwt import decode_jwt_token, generate_access_token_from_refresh_token
import time

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('Authorization')
        refresh_token = request.COOKIES.get('Refresh')

        if not access_token:
            return None

        payload = decode_jwt_token(access_token)
        if not payload:
            return None

        # Check if this is a temporary token
        if payload.get('type') == 'temp':
            # Only allow access to MFA verification endpoints
            if request.path.endswith('login/'):
                response = ApiResponse()
                response.delete_cookie('Authorization')
                return response
                
            if not request.path.endswith(('mfa/verify/', 'mfa/qr-code/', 'mfa/enable/')):
                raise exceptions.AuthenticationFailed('MFA verification required')
            
            user_id = payload.get('user_id')
            try:
                user = User.objects.get(pk=user_id)
                return (user, None)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('No such user')

        # Handle regular access tokens
        # If access token is expired or will expire soon (within 1 minute)
        if payload.get('exp', 0) - time.time() < 60:
            # Try to refresh using refresh token
            if refresh_token:
                new_access_token = generate_access_token_from_refresh_token(refresh_token)
                if new_access_token:
                    request.new_access_token = new_access_token
                    payload = decode_jwt_token(new_access_token)
                else:
                    return None
            else:
                return None

        user_id = payload.get('user_id')
        if not user_id:
            return None

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        if user.mfa_enabled:
            # Check if the token has MFA claim
            if 'mfa' not in payload or not payload['mfa']:
                raise exceptions.AuthenticationFailed('MFA verification needed')

        return (user, None)  # Authentication successful

    def authenticate_header(self, request):
        return 'Bearer'
