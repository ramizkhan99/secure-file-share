from django.urls import reverse
from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser
from users.role import UserRole

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user and request.user.is_admin
    
class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False
        return request.user and request.user.is_regular_user
    
class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.is_authenticated

class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:

        # Allow user registration without authentication
        if hasattr(view, 'action') and view.action == 'create':
            return True
        
        # Define permissions by role and method
        role_permissions = {
            UserRole.ADMIN: {
                'GET': True,      # Can view all users
                'POST': True,     # Can create users
                'PUT': True,      # Can update users
                'PATCH': True,    # Can partially update users
                'DELETE': True,   # Can delete users
            },
            UserRole.USER: {
                'GET': True,      # Can view own profile
                'PUT': True,      # Can update own profile
                'PATCH': True,    # Can partially update own profile
                'DELETE': False,  # Cannot delete users
            },
            UserRole.GUEST: {
                'GET': True,      # Can only view own profile
                'PUT': False,     # Cannot update
                'PATCH': False,   # Cannot update
                'DELETE': False,  # Cannot delete
            }
        }
        return role_permissions.get(request.user.role, {}).get(request.method, False)

    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, AnonymousUser):
            return False

        # Admin can do anything
        if request.user.role == UserRole.ADMIN:
            return True
            
        # Users can only access their own profile
        return obj.id == request.user.id