from django.conf import settings

class JWTRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # If a new access token was generated during authentication
        if hasattr(request, 'new_access_token'):
            response.set_cookie(
                'Authorization',
                request.new_access_token,
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=settings.JWT_EXPIRATION_TIME
            )
        
        return response 