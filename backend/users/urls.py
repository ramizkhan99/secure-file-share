from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login, enable_mfa, logout, mfa_qr_code, verify_mfa

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('mfa/verify/', verify_mfa, name='verify_mfa'),
    path('mfa/enable/', enable_mfa, name='enable_mfa'),
    path('mfa/qr-code/', mfa_qr_code, name='mfa_qr_code'),
    path('', include(router.urls)),
]