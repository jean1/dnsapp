from rest_framework import permissions, status
from core.models import Rr, Zone, Zonerule, Namespace, PermNamespace, PermZone, PermRr
from core.serializers import RrSerializer
from rest_framework.exceptions import ValidationError

# For each viewset, permission_classes are defined.
# For each view,  permission classes wil be checked.
# Permission classes have 2 methods, depending on request :
# - has_object_permission for GET, DELETE, PUT
# - has_permission for POST (create)
#
# NB: When listing a collection, by default, *no* permission class is
# called, for performance reasons
# Allowed objects list must be build by joining object and permission tables

# Example call flow :
#
# POST /zone/
# view create
#   for pc in permission_classes: [ZoneAccess, ZoneCreate]
#       if ZoneAccess.has_permission: (method does not exist)
#       if ZoneCreate.has_permission: ...
#  
# POST /rr/
# view create
#   for pc in permission_classes: [RrAccess, RrValidNameOrType]
#       if RrAccess.has_permission: ...
#       if RrValidNameOrType.has_permission: ...
#
# GET /rr/1
# view retrieve
#   for pc in permission_classes: [RrAccess]
#       if RrAccess.has_object_permission: ...
#

# Permission for Namespace
#
# View / Permission that must be checked :
# list               (GET /)      list all namespaces    -> check AccessNamespace for each namespace or admin
# retrieve           (GET /1)     retrieve 1 namespace   -> check AccessNamespace for this namespace or admin
# destroy            (DELETE /1)  destroy 1 namespace    -> admin OK ; denied if not admin
# update             (PUT /1)     update  1 namespace    -> admin OK ; denied if not admin
# create             (POST)       create  1 namespace    -> admin OK ; denied if not admin
# partial_update     (PATCH /1)                             NOT IMPLEMENTED
#

class NamespaceAccess(permissions.BasePermission):
   def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:   
            return True
        groups = request.user.groups.all()
        permission = PermNamespace.objects.filter(group__in = groups).filter(action='AccessNamespace')
        return permission.filter(namespace = obj).exists()

   def allowed_namespaces(user):
        '''
            This method is used for retrieving list of all allowed namespace for a given user
            Normally called from view 'list' in NamespaceViewset
        '''
        if user.is_superuser:   
            return Namespace.objects.all()
        # Fetch all groups for user
        groups = user.groups.all()
        # Fetch set of permissions for all groups which match access permission
        permission = PermNamespace.objects.filter(group__in = groups).filter(action='AccessNamespace').all()
        # Return all namespaces matching permissions
        return Namespace.objects.filter(permnamespace__in = permission)

#
# Permission for Zone
#
# View / Permission that must be checked :
# list               (GET /)      list all zone     -> check AccessZone for all zones or admin
# retrieve           (GET /1)     retrieve 1 zone   -> check AccessZone for this zone or admin
# destroy            (DELETE /1)  destroy 1 zone    -> check DeleteZone for this zone or admin
# update             (PUT /1)     update  1 zone    -> check UpdateZone for this zone or admin
# create             (POST)       create  1 zone    -> check PermNamespace.CreateZoneInNamespace for namespace or admin 
# partial_update     (PATCH /1)                     NOT IMPLEMENTED
#

class ZoneAccess(permissions.BasePermission):
   def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:   
            return True
        # FIXME: implement permission checking
        groups = request.user.groups.all()
        permission = PermZone.objects.filter(group__in = groups).filter(action='AccessZone')
        return permission.filter(zone = obj).exists()

   def allowed_zone(user):
        '''
            This method is used for retrieving list of all allowed zone for a given user
            Normally called from view 'list' in ZoneViewset
        '''
        if user.is_superuser:   
            return Zone.objects.all()
        # Fetch all groups for user
        groups = user.groups.all()
        # Fetch set of permissions for all groups which match access permission
        permission = PermZone.objects.filter(group__in = groups).filter(action='AccessZone').all()
        # Return all zone matching permissions
        return Zone.objects.filter(permzone__in = permission)

class ZoneCreate(permissions.BasePermission):
   def has_permission(self, request, view):
        if request.user.is_superuser:   
            return True
        serializer = RrSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        n = serializer.validated_data['namespace']
        g = request.user.group
        a = 'CreateZoneInNamespace'
        permission = PermNamespace.objects.filter(namespace=n, action=a, group=g)
        return permission.exists()

#
# Permission for Rr
#
# View / Permission that must be checked :
# list               (GET /)      list all rr       -> filter rr only with perm "AccessRr" or all if admin
# retrieve           (GET /1)     retrieve 1 zone   -> check AccessRr for this Rr or admin
# destroy            (DELETE /1)  destroy 1 zone    -> check UpdateDeleteRr for this Rr or admin
# update             (PUT /1)     update  1 zone    -> check UpdateDeleteRr for this Rr or admin
# create             (POST)       create  1 zone    -> check PermZone.CreateRrInZone for zone + check RrValidNameOrType rules for zone or admin
# partial_update     (PATCH /1)                     NOT IMPLEMENTED
#

class RrAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:   
            return True
        # FIXME: fetch permission
        pass

    def has_permission(self, request, view):
        if request.user.is_superuser:   
            return True
        # FIXME: check PermZone.CreateRrInZone
        pass

class RrValidNameOrType(permissions.BasePermission):
    """
    Check Rr name and type at Rr creation
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        serializer = RrSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data['name']
        type = serializer.validated_data['type']
        zone = serializer.validated_data['zone']
        rule = Zonerule.objects.get(zone=zone)
        # No rule defined for this zone: permission granted
        if not rule:
            return True

        return rule.is_checked(name, type)

