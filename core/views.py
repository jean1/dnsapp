from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from core.models import (Namespace, Zone, Rr, Zonerule,
                         PermNamespace, PermZone, PermRr)
from core.serializers import NamespaceSerializer, ZoneSerializer, RrSerializer
from core.permissions import (PermCheck, NamespacePermCheck, RrPermCheck,
        get_allowed_rrs, set_perm, get_allowed_namespaces, get_allowed_zones)
from rest_framework.response import Response

# 
# Utility functions
# 

def get_namespace_or_404(pk):
    try:
        return Namespace.objects.get(pk=pk)
    except Namespace.DoesNotExist:
        raise Http404

def get_zone_or_404(pk):
    try:
        return Zone.objects.get(pk=pk)
    except Zone.DoesNotExist:
        raise Http404

def get_rr_or_404(pk):
    try:
        return Rr.objects.get(pk=pk)
    except Rr.DoesNotExist:
        raise Http404


#
# Permission for Namespace
#
# View / Permission that must be checked :
# list               (GET /)      list all namespaces    -> check "read" for each namespace or admin
# retrieve           (GET /1)     retrieve 1 namespace   -> check "read" for this namespace or admin
# destroy            (DELETE /1)  destroy 1 namespace    -> admin OK ; denied if not admin
# update             (PUT /1)     update  1 namespace    -> admin OK ; denied if not admin
# create             (POST)       create  1 namespace    -> admin OK ; denied if not admin
# partial_update     (PATCH /1)                             NOT IMPLEMENTED
#

class NamespaceDetail(APIView):
    def get(self, request, pk, format=None):
        namespace = get_namespace_or_404(pk)
        # Check permission
        if not PermCheck.can_get(request.user, namespace, PermNamespace):
           raise PermissionDenied('namespace get unauthorized')
        serializer = NamespaceSerializer(namespace)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        namespace = get_namespace_or_404(pk)

        # Check permission
        if not NamespacePermCheck.can_delete(request.user):
           raise PermissionDenied('namespace delete unauthorized')

        namespace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        namespace = get_namespace_or_404(pk)
        serializer = NamespaceSerializer(namespace, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        if not NamespacePermCheck.can_update(request.user):
           raise PermissionDenied('namespace update unauthorized')

        serializer.save()
        return Response(serializer.data)

class NamespaceListOrCreate(APIView):
    def get(self, request, format=None):
        namespaces = get_allowed_namespaces(request.user, "r")
        serializer = NamespaceSerializer(namespaces, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = NamespaceSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not NamespacePermCheck.can_create(request.user):
           raise PermissionDenied('namespace create unauthorized for this namespace')

        serializer.save()

        # FIXME: add a permission to created namespace
        # NamespacePermCheck.add(request.user, serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

#
# Permission for Zone
#
# View / Permission that must be checked :
# list               (GET /)      list all zones    -> check "read" for all zones or admin
# retrieve           (GET /1)     retrieve 1 zone   -> check "read" for this zone or admin
# destroy            (DELETE /1)  destroy 1 zone    -> check "write" for this zone or admin
# update             (PUT /1)     update  1 zone    -> check "write" for this zone or admin
# create             (POST)       create  1 zone    -> check PermNamespace."createrecord" for namespace or admin
# partial_update     (PATCH /1)                     NOT IMPLEMENTED
#


class ZoneDetail(APIView):

    def get(self, request, pk, format=None):
        zone = get_zone_or_404(pk)

        #import ipdb; ipdb.set_trace()

        # Check permission
        if not PermCheck.can_get(request.user, zone, PermZone):
           raise PermissionDenied('zone get unauthorized')

        serializer = ZoneSerializer(zone)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        zone = get_zone_or_404(pk)

        # Check permission
        if not PermCheck.can_delete(request.user, zone, PermZone):
           raise PermissionDenied('zone delete unauthorized')

        zone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        zone = get_zone_or_404(pk)

        serializer = ZoneSerializer(zone, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        if not PermCheck.can_update(request.user, zone, PermZone):
           raise PermissionDenied('zone update unauthorized')

        serializer.save()
        return Response(serializer.data)

class ZoneListOrCreate(APIView):
    def get(self, request, format=None):
        zones = get_allowed_zones(request.user, "rg")
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ZoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        namespace = serializer.validated_data['namespace']
        if not PermCheck.can_create_record(request.user, namespace, PermNamespace):
           raise PermissionDenied('zone create unauthorized for this namespace')

        serializer.save()

        # FIXME: add "rw" permission to created zone

        return Response(serializer.data, status=status.HTTP_201_CREATED)

#
# View / Permission that must be checked :
# list               (GET /)      list all rr     -> filter rr only with perm "GetRr" or all if admin
# retrieve           (GET /1)     retrieve 1 rr   -> check GetRr for this Rr or admin
# destroy            (DELETE /1)  destroy 1 rr    -> check UpdateDeleteRr for this Rr or admin
# update             (PUT /1)     update  1 rr    -> check UpdateDeleteRr for this Rr or admin
# create             (POST)       create  1 rr    -> check PermZone.CreateRrInZone for zone + check RrValidNameOrType rules for zone or admin
# partial_update     (PATCH /1)                     NOT IMPLEMENTED

class RrDetail(APIView):
    def get(self, request, pk, format=None):
        rr = get_rr_or_404(pk)

        # Check permission
        # import ipdb; ipdb.set_trace()
        if not PermCheck.can_get(request.user, rr, PermRr):
           raise PermissionDenied('rr get unauthorized')

        serializer = RrSerializer(rr)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        rr = get_rr_or_404(pk)

        # Check permission
        if not PermCheck.can_delete(request.user, rr, PermRr):
           raise PermissionDenied('rr delete unauthorized')

        rr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        rr = get_rr_or_404(pk)

        serializer = RrSerializer(rr, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        if not PermCheck.can_update(request.user, rr, PermRr):
           raise PermissionDenied('rr update unauthorized')

        serializer.save()
        return Response(serializer.data)


class ZoneRrList(APIView):
    def get(self, request, pk, format=None):

        zone = get_zone_or_404(pk)

        if PermCheck.can_generate(request.user, zone, PermZone):
            rrs = Rr.objects.all()
        else:
            rrs = get_allowed_rrs(request.user, "r")
            rrs = rrs.filter(zone=zone)

        serializer = RrSerializer(rrs, many=True)
        return Response(serializer.data)


class RrListOrCreate(APIView):
    def get(self, request, format=None):
        rrs = get_allowed_rrs(request.user, "r")
        serializer = RrSerializer(rrs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RrSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permissions
        zone = serializer.validated_data['zone']
        name = serializer.validated_data['name']
        type = serializer.validated_data['type']

        # DEBUG
        #print(f'DEBUG RrListOrCreate view ; name={name}')
        #import ipdb; ipdb.set_trace()
        # DEBUG

        if not PermCheck.can_create_record(request.user, zone, PermZone):
           raise PermissionDenied('rr create unauthorized for this zone')

        if not RrPermCheck.can_create_when_name_exist(request.user, name, type):
           raise PermissionDenied("rr create unauthorized: rr with same name and type already exists and is not updatable by user")

        if not RrPermCheck.can_create_by_rule(request.user, name, zone, type):
           raise PermissionDenied("rr create unauthorized: name or type invalid by rule")

        # Check if CNAME and name already exists in zone
        if type == "CNAME":
            if Rr.objects.filter(name=name, zone=zone).exists():
                raise ValidationException(detail=f"Can't create CNAME '{name}' because name already exist")
        # Check if name already exists in zone as CNAME
        if Rr.objects.filter(name=name, zone=zone, type="CNAME").exists():
            raise ValidationException(detail=f"Can't create '{name}' because CNAME with same name already exist")

        # Record Rr in database
        rr = serializer.save()

        # Set permission on created rr for user
        set_perm(request.user, rr, PermRr, "rw")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

