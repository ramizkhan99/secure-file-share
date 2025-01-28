from http import HTTPStatus
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from common.apiresponse import ApiResponse
from .models import User
from .serializers import UserSerializer
from common.jwt import generate_jwt_tokens, generate_access_token_from_refresh_token, generate_temp_token, decode_jwt_token
from io import BytesIO
import pyqrcode
from django.http import HttpResponse
from rest_framework import exceptions
from .permissions import RoleBasedPermission
from django.conf import settings

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [RoleBasedPermission]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                response = Response({
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
                token = generate_jwt_tokens(user)
                response.set_cookie(
                    'Authorization', 
                    token[0],
                    httponly=True,
                    secure=True,
                    samesite='None',
                    max_age=settings.JWT_EXPIRATION_TIME  # Add max_age to match JWT expiration
                )
                response.set_cookie(
                    'Refresh', 
                    token[1],
                    httponly=True,
                    secure=True,
                    samesite='None',
                    max_age=settings.JWT_REFRESH_EXPIRATION_TIME
                )
                return response
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return User.objects.none()
        if user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=user.id)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """View for user login and JWT token generation."""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    
    if user is not None and isinstance(user, User):
        if user.mfa_enabled:
            # Generate temporary token for MFA verification
            temp_token = generate_temp_token(user)
            response = ApiResponse(
                success=True,
                message='MFA verification required',
                status_code=HTTPStatus.ACCEPTED,
                code='MFA_REQUIRED'
            )
            response.set_cookie(
                'Authorization',
                temp_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=300  # 5 minutes
            )
            return response
        else:
            # No MFA, generate full tokens
            access_token, refresh_token = generate_jwt_tokens(user, mfa_verified=True)
            response = ApiResponse(
                success=True,
                message='Login successful',
                status_code=HTTPStatus.OK,
                data={
                    'username': username,
                    'email': user.email,
                    'role': user.role,
                    'isMFAEnabled': False
                }
            )
            response.set_cookie(
                'Authorization',
                access_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=settings.JWT_EXPIRATION_TIME
            )
            response.set_cookie(
                'Refresh',
                refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=settings.JWT_REFRESH_EXPIRATION_TIME
            )
            return response
    else:
        return ApiResponse(
            success=False,
            message='Invalid credentials',
            status_code=HTTPStatus.UNAUTHORIZED,
            code='INVALID_CREDENTIALS'
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_mfa(request):
    """Verify MFA token and upgrade temporary token to full JWT"""
    temp_token = request.COOKIES.get('Authorization')
    mfa_token = request.data.get('token')

    if not temp_token or not mfa_token:
        return ApiResponse(
            success=False,
            message='Missing token',
            status_code=HTTPStatus.BAD_REQUEST,
            code='MISSING_TOKEN'
        )

    # Verify temporary token
    payload = decode_jwt_token(temp_token)
    if not payload or payload.get('type') != 'temp':
        return ApiResponse(
            success=False,
            message='Invalid temporary token',
            status_code=HTTPStatus.UNAUTHORIZED,
            code='INVALID_TEMP_TOKEN'
        )

    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return ApiResponse(
            success=False,
            message='User not found',
            status_code=HTTPStatus.UNAUTHORIZED,
            code='USER_NOT_FOUND'
        )

    # Verify MFA token
    if not user.verify_totp(mfa_token):
        return ApiResponse(
            success=False,
            message='Invalid MFA token',
            status_code=HTTPStatus.UNAUTHORIZED,
            code='INVALID_MFA_TOKEN'
        )

    # Generate full tokens only if MFA is verified
    access_token, refresh_token = generate_jwt_tokens(user, mfa_verified=True)
    
    response = ApiResponse(
        success=True,
        message='MFA verified successfully',
        status_code=HTTPStatus.OK,
        data={
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'isMFAEnabled': True
        }
    )
    
    response.set_cookie(
        'Authorization',
        access_token,
        httponly=True,
        secure=True,
        samesite='None',
        max_age=settings.JWT_EXPIRATION_TIME
    )
    response.set_cookie(
        'Refresh',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='None',
        max_age=settings.JWT_REFRESH_EXPIRATION_TIME
    )
    return response

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.user.is_anonymous:
        return Response({'message': 'Please login first'}, status=HTTPStatus.ACCEPTED)

    request.user.mfa_verified = False
    request.user.save()
    
    response = ApiResponse(
        status_code=HTTPStatus.ACCEPTED,
        message='Logout successful',
        code='LOGOUT_SUCCESS'
    )
    response.delete_cookie('Authorization')
    response.delete_cookie('Refresh')
    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_mfa(request):
    """Enables MFA for the user and generates TOTP secret."""
    user = request.user
    
    if user.mfa_enabled:
        return ApiResponse(
            success=False,
            message='MFA is already enabled',
            status_code=HTTPStatus.BAD_REQUEST,
            code='MFA_ALREADY_ENABLED'
        )
    
    user.generate_totp_secret()
    user.mfa_enabled = True
    user.save()
    
    # Generate temporary token for QR code access
    temp_token = generate_temp_token(user)
    
    response = ApiResponse(
        success=True,
        message='MFA enabled successfully',
        status_code=HTTPStatus.OK,
        code='MFA_ENABLED'
    )
    
    # Set temporary token cookie
    response.set_cookie(
        'Authorization',
        temp_token,
        httponly=True,
        secure=True,
        samesite='None',
        max_age=300  # 5 minutes
    )
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def mfa_qr_code(request) -> (Response | HttpResponse):
    """Generates a QR code for TOTP setup."""
    temp_token = request.COOKIES.get('Authorization')
    
    if not temp_token:
        return ApiResponse(
            success=False,
            message='Missing token',
            status_code=HTTPStatus.BAD_REQUEST,
            code='MISSING_TOKEN'
        )

    # Verify temporary token
    payload = decode_jwt_token(temp_token)
    if not payload or payload.get('type') != 'temp':
        return ApiResponse(
            success=False,
            message='Invalid temporary token', 
            status_code=HTTPStatus.UNAUTHORIZED,
            code='INVALID_TEMP_TOKEN'
        )

    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return ApiResponse(
            success=False,
            message='User not found',
            status_code=HTTPStatus.UNAUTHORIZED,
            code='USER_NOT_FOUND'
        )
    
    if not user.mfa_enabled:
        return ApiResponse(
            success=False,
            message='MFA not enabled for user',
            status_code=HTTPStatus.BAD_REQUEST,
            code='MFA_NOT_ENABLED'
        )
    
    uri = user.get_totp_uri()
    qr = pyqrcode.create(uri)
    buffer = BytesIO()
    qr.png(buffer, scale=6)

    return HttpResponse(buffer.getvalue(), content_type="image/png")