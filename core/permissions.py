from rest_framework import permissions

class HasAccess(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it
    """
    def has_object_permission(self, request, view, obj):
        perm = f"access_{type(obj).__name__.lower()}"
        if request.user.has_perm(perm, obj):
            return True
        return False
