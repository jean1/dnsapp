from rest_framework import status
from rest_framework import permissions
from core.models import Rr, Zone, Zonerule, Namespace, PermNamespace, PermZone, PermRr
from core.serializers import RrSerializer, ZoneSerializer
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
        # import ipdb; ipdb.set_trace()
        if request.user.is_superuser:   
            return True
        groups = request.user.groups.all()
        permission = PermNamespace.objects.filter(group__in = groups).filter(action='AccessNamespace')
        return permission.filter(namespace = obj).exists()

    def has_permission(self, request, view):
        if request.user.is_superuser:   
            return True
        if request.method in permissions.SAFE_METHODS and \
            bool(request.user and request.user.is_authenticated):
            return True
        return False

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
# list               (GET /)      list all zone     -> check GetZone for all zones or admin
# retrieve           (GET /1)     retrieve 1 zone   -> check GetZone for this zone or admin
# destroy            (DELETE /1)  destroy 1 zone    -> check DeleteZone for this zone or admin
# update             (PUT /1)     update  1 zone    -> check UpdateZone for this zone or admin
# create             (POST)       create  1 zone    -> check PermNamespace.CreateZoneInNamespace for namespace or admin 
# partial_update     (PATCH /1)                     NOT IMPLEMENTED
#

class ZonePermCheck():
    def check_permission(user, zone, action):
        '''
        Generic function to check permission flag for a zone
        '''
        if user.is_superuser:   
            return True
        groups = user.groups.all()
        # PermZone describes permission on a zone as a triplet (zone, group, action) 
        # Example: PermZone("example.com","group1","GetZone")
        permissions = PermZone.objects.filter(zone=zone).filter(action=action).all()
        return permissions.filter(group__in = groups).exists()

    def allowed_zones(user):
        '''
            Retrieves list of all allowed zone for a given user
            Normally called from view 'list' in ZoneViewset
        '''
        if user.is_superuser:
            return Zone.objects.all()
        # Fetch all groups for user
        groups = user.groups.all()
        # Fetch set of permissions for all groups which match access permission
        permission = PermZone.objects.filter(group__in = groups).filter(action='GetZone').all()
        # Return all zone matching permissions
        return Zone.objects.filter(permzone__in = permission)

    def can_get(user, zone):
        return ZonePermCheck.check_permission(user, zone, 'GetZone')

    def can_update(user, zone):
        return ZonePermCheck.check_permission(user, zone, 'UpdateZone')

    def can_delete(user, zone):
        return ZonePermCheck.check_permission(user, zone, 'DeleteZone')

    def can_create_in_namespace(user, namespace):
        groups = user.groups.all()
        action = 'CreateZoneInNamespace'
        permissions = PermNamespace.objects.filter(namespace=namespace).filter(action=action).all()
        return permissions.filter(group__in = groups).exists()

#
# Permission for Rr
#
# View / Permission that must be checked :
# list               (GET /)      list all rr     -> filter rr only with perm "GetRr" or all if admin
# retrieve           (GET /1)     retrieve 1 rr   -> check GetRr for this Rr or admin
# destroy            (DELETE /1)  destroy 1 rr    -> check UpdateDeleteRr for this Rr or admin
# update             (PUT /1)     update  1 rr    -> check UpdateDeleteRr for this Rr or admin
# create             (POST)       create  1 rr    -> check PermZone.CreateRrInZone for zone + check RrValidNameOrType rules for zone or admin
# partial_update     (PATCH /1)                     NOT IMPLEMENTED
#
class RrPermCheck():
    def check_permission(user, rr, action):
        '''
        Generic function to check permission flag for a zone
        '''
        if user.is_superuser:   
            return True
        groups = user.groups.all()
        # PermRr describes permission on a zone as a triplet (rr, group, action) 
        # Example: PermRr("www","group1","GetRr")
        permissions = PermRr.objects.filter(rr=rr).filter(action=action).all()
        return permissions.filter(group__in = groups).exists()

    def allowed_rr(user):
        '''
            Retrieves list of all allowed rr for a given user
            Normally called from view 'list' in RrViewset
        '''
        if user.is_superuser:
            return Rr.objects.all()
        # Fetch all groups for user
        groups = user.groups.all()
        # Fetch set of permissions for all groups which match access permission
        permission = PermRr.objects.filter(group__in = groups).filter(action='GetRr').all()
        # Return all rr matching permissions
        return Rr.objects.filter(permrr__in = permission)

    def can_get(user, rr):
        return RrPermCheck.check_permission(user, rr, 'GetRr')

    def can_update(user, rr):
        return RrPermCheck.check_permission(user, rr, 'UpdateDeleteRr')

    def can_delete(user, rr):
        return RrPermCheck.check_permission(user, rr, 'UpdateDeleteRr')

    # When creating a new RR, check if RR with same name and same type
    # already exist and if user has update permission on them
    # Example: add new RR (abc,A,192.0.1.2) and an RR (abc,A,192.0.1.222) already exists
    #          -> user must have permission on second RR

    def can_create_when_name_exist(user, name, type):
        """
        Check if all Rr with same name and same type
        are allowed for update/delete to a given user
        Example:
            user 'joe' is in group g1 and g2 and wants to create RR(abc,A,192.0.1.99)
            existing permissions:
                RR (abc,A,192.0.1.222), action=UpdateDeleteRr, group g1
                RR (abc,A,192.0.1.111), action=UpdateDeleteRr, group g2
            -> access granted
        """
        if user.is_superuser:   
            return True

        groups = user.groups.all()
        for rr in Rr.objects.filter(name=name, type=type):
            if not PermRr.objects.filter(group__in = groups).filter(rr=rr,action='UpdateDeleteRr').exists():
                return False
        return True

    def can_create_by_rule(user, name, type):
        if user.is_superuser:
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

    def can_create_in_zone(user, zone):
        groups = user.groups.all()
        action = 'CreateRrInZone'
        permissions = PermZone.objects.filter(zone=zone).filter(action=action).all()
        return permissions.filter(group__in = groups).exists()
