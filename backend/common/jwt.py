import jwt
import time
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_temp_token(user):
    """Generate a short-lived token for MFA verification"""
    payload = {
        'user_id': user.id,
        'exp': int(time.time()) + 300,  # 5 minutes expiry
        'iat': int(time.time()),
        'type': 'temp',
        'mfa': False
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def generate_jwt_tokens(user, mfa_verified=True):
    """Generates both access and refresh tokens for the given user."""
    # Access token with shorter lifetime
    access_payload = {
        'user_id': user.id,
        'exp': int(time.time()) + settings.JWT_EXPIRATION_TIME,
        'iat': int(time.time()),
        'mfa': mfa_verified,
        'type': 'access'
    }
    
    # Refresh token with longer lifetime
    refresh_payload = {
        'user_id': user.id,
        'exp': int(time.time()) + settings.JWT_REFRESH_EXPIRATION_TIME,
        'iat': int(time.time()),
        'jti': str(uuid.uuid4()),
        'mfa': mfa_verified,
        'type': 'refresh'
    }
    
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    
    return access_token, refresh_token

def decode_jwt_token(token):
    """Decodes a JWT token and returns the payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_access_token_from_refresh_token(refresh_token):
    """Generates a new access token using a valid refresh token."""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        
        if payload.get('type') != 'refresh':
            return None
            
        user = User.objects.get(id=payload['user_id'])
        mfa_verified = payload.get('mfa', False)
        
        access_payload = {
            'user_id': user.id,
            'exp': int(time.time()) + settings.JWT_EXPIRATION_TIME,
            'iat': int(time.time()),
            'mfa': mfa_verified,
            'type': 'access'
        }
        
        return jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None