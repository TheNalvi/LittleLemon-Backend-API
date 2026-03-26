from rest_framework import permissions

class isManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (
            request.user.is_authenticated and request.user.groups.filter(name='manager').exists()
        )
        
class isManagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.groups.filter(name='manager').exists())