from rest_framework import status
from rest_framework import permissions
from core.models import Rr, Zone, Zonerule, Namespace, PermRr, PermNamespace, PermZone
from core.serializers import RrSerializer, ZoneSerializer
from rest_framework.exceptions import ValidationError

def check_permission(user, obj, permobj, action):
    '''
    Generic function to check ONE permission flag for an object and for a user
    '''
    if user.is_superuser:
        return True

## DEBUG
#    print("obj")
#    print(obj)

    # Get all groups
    groups = user.groups.all()
## DEBUG
#    print("groups")
#    print(groups)

    # Join all permissions for given object and given flag
    permissions = permobj.objects.filter(obj=obj).filter(action__icontains=action).all()
## DEBUG
#    print("permissions")
#    print(permissions)

    # Join found permissions with found groups 
    filteredpermissions = permissions.filter(group__in = groups)
## DEBUG
#    print("filteredpermissions")
#    print(filteredpermissions)

    result = filteredpermissions.exists()

## DEBUG
#    print("result")
#    print(result)

    return result

def get_perms(user, objtype, permobj, action):
    '''
        Retrieves list of all allowed objects for a given user, based on permission
        Normally called from view 'list'
    '''
    # Fetch all groups for user
    groups = user.groups.all()
    # Fetch set of permissions for all groups which match access permission
    return permobj.objects.filter(group__in = groups).filter(action__icontains=action).all()

def set_perm(user, obj, permobj, action):
    '''
        Create a permission entry for given object, user, action
        Normally called from view 'post'
    '''
    # 1) Pref(user, zone, group, action)
    # on cree un RR -> cherche la preference pour (user,zone)
    #               -> exemple : on a trouvé Pref(group="gr1",action="update")
    #                                        Pref(group="gr1",action="delete")
    #               -> on cree 2 objets PermRR(rr_créé, "gr1","update") , PermRR(rr_créé, "gr1","delete") 
    # 2) if no pref defined, use default_pref from user model

    # FIXME: test if Pref exist for user/zone
    #
    # if ... pref ... :
    #   pref = ....
    # else:
    pref = user.default_pref

    permobj.objects.create(obj = obj, group = pref, action = action)

def get_allowed_namespaces(user, action):
    '''
        extract readable namespaces for user
    '''
    if user.is_superuser:
        return Namespace.objects.all()
    perms = get_perms(user, Namespace, PermNamespace, "r")
    return Namespace.objects.filter(permnamespace__in = perms)

def get_allowed_zones(user, action):
    '''
        extract readable zones for user
    '''
    if user.is_superuser:
        return Zone.objects.all()
    perms = get_perms(user, Zone, PermZone, "r") 
    return Zone.objects.filter(permzone__in = perms)

def get_allowed_rrs(user, action):
    '''
        extract readable rr for user
    '''
    if user.is_superuser:
        return Rr.objects.all()
    perms =  get_perms(user, Rr, PermRr, "r")
    return Rr.objects.filter(permrr__in = perms)

class PermCheck():
    '''
        generic methods to check permission
    '''
    def can_get(user, obj, permobj):
        r = check_permission(user, obj, permobj, "r")
## DEBUG
#        print("result of can_get")
#        print(r)

        return r

    def can_update(user, obj, permobj):
        if user.is_superuser:
            return True
        return check_permission(user, obj, permobj, "w")

    def can_delete(user, obj, permobj):
        if user.is_superuser:
            return True
        return check_permission(user, obj, permobj, "w")

    def can_create_record(user, obj, permobj):
        if user.is_superuser:
            return True
        groups = user.groups.all()
        permissions = permobj.objects.filter(obj=obj).filter(action__icontains="c").all()
        return permissions.filter(group__in = groups).exists()

class NamespacePermCheck(PermCheck):

    def can_delete(user):
        return user.is_superuser

    def can_update(user):
        return user.is_superuser

    def can_create(user):
        return user.is_superuser

class RrPermCheck():

    def can_create_when_name_exist(user, name, type):
        """
        Check if all Rr with same name and same type
        are allowed for write to a given user
        Example:
            user 'joe' is in group g1 and g2 and wants to create RR(abc,A,192.0.1.99)
            existing permissions:
                RR3 (abc,A,192.0.1.222), action="w", group g1
                RR4 (abc,A,192.0.1.111), action="w", group g2
            -> access granted because all other RR with same name/type are writable
        """
        if user.is_superuser:   
            return True

        # DEBUG
        #print(f"DEBUG can_create_when_name_exist, name={name}")
        #import ipdb; ipdb.set_trace()

        groups = user.groups.all()
        for rr in Rr.objects.filter(name=name, type=type):
            if not PermRr.objects.filter(group__in = groups).filter(obj=rr,action__icontains="w").exists():
                return False
        return True

    def can_create_by_rule(user, name, zone, type):
        if user.is_superuser:
            return True

        for rule in Zonerule.objects.filter(zone=zone):
            if not rule.is_checked(name, type):
                return False
        # No rule defined for this zone: permission granted
        #
        # FIXME:
        # make at least one rule mandatory, following the least priviledge principle ?
        # or document that this feature is only needed for shared zones ?
        #
        return True

