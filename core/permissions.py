from rest_framework import permissions
from core.models import Rr, Zone, Zonerule
from core.serializers import RrSerializer

class HasAccess(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it
    """
    def has_object_permission(self, request, view, obj):
        perm = f"access_{type(obj).__name__.lower()}"
        if request.user.has_perm(perm, obj):
            return True
        return False

class RrValidNameOrType(permissions.BasePermission):
    """
    Custom permission to apply rule to zone
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        serializer = RrSerializer(data=request.data)
        # Wrong data: permission denied
        if not serializer.is_valid():
            return False

        name = serializer.validated_data['name']
        type = serializer.validated_data['type']
        zone = serializer.validated_data['zone']
        rule = Zonerule.objects.get(zone=zone)
        # No rule defined for this zone: permission granted
        if not rule:
            return True

        return rule.is_checked(name, type)
