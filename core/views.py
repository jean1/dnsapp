from django.db.models.query import QuerySet
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from core.models import Namespace, Zone, Rr, Zonerule, PermNamespace, PermZone, PermRr
from core.serializers import NamespaceSerializer, ZoneSerializer, RrSerializer
from core.permissions import NamespaceAccess, ZonePermCheck, RrPermCheck
from rest_framework.response import Response

class NamespaceViewSet(viewsets.ModelViewSet):
    serializer_class = NamespaceSerializer
    permission_classes = [NamespaceAccess]
    queryset = Namespace.objects.all()
    
    def list(self, request):
        # import ipdb; ipdb.set_trace()
        queryset = NamespaceAccess.allowed_namespaces(request.user)
        serializer = NamespaceSerializer(queryset, many=True)
        return Response(serializer.data)
        
class ZoneDetail(APIView):
    def get_zone_or_404(self, pk):
        try:
            return Zone.objects.get(pk=pk)
        except Zone.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        zone = self.get_zone_or_404(pk)

        #import ipdb; ipdb.set_trace()

        # Check permission
        if not ZonePermCheck.can_get(request.user, zone):
           raise PermissionDenied('zone get unauthorized')

        serializer = ZoneSerializer(zone)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        zone = self.get_zone_or_404(pk)

        # Check permission
        if not ZonePermCheck.can_delete(request.user, zone):
           raise PermissionDenied('zone delete unauthorized')

        zone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        zone = self.get_zone_or_404(pk)
        
        serializer = ZoneSerializer(zone, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        if not ZonePermCheck.can_update(request.user, zone):
           raise PermissionDenied('zone update unauthorized')

        serializer.save()
        return Response(serializer.data)

class ZoneListOrCreate(APIView):
    def get(self, request, format=None):
        '''
        List all allowed zones 
        '''
        zones = ZonePermCheck.allowed_zones(request.user)
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ZoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        namespace = serializer.validated_data['namespace']
        if not ZonePermCheck.can_create_in_namespace(request.user, namespace):
           raise PermissionDenied('zone create unauthorized for this namespace')

        serializer.save()

        # FIXME: add permission to created objects

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
    def get_rr_or_404(self, pk):
        try:
            return Rr.objects.get(pk=pk)
        except Rr.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        rr = self.get_rr_or_404(pk)

        #import ipdb; ipdb.set_trace()

        # Check permission
        if not RrPermCheck.can_get(request.user, rr):
           raise PermissionDenied('rr get unauthorized')

        serializer = RrSerializer(rr)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        rr = self.get_rr_or_404(pk)

        # Check permission
        if not RrPermCheck.can_delete(request.user, rr):
           raise PermissionDenied('rr delete unauthorized')

        rr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        rr = self.get_rr_or_404(pk)
        
        serializer = RrSerializer(rr, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check permission
        if not RrPermCheck.can_update(request.user, rr):
           raise PermissionDenied('rr update unauthorized')

        serializer.save()
        return Response(serializer.data)

class RrListOrCreate(APIView):
    def get(self, request, format=None):
        '''
        List all allowed rr 
        '''
        #import ipdb; ipdb.set_trace()
        rrs = RrPermCheck.allowed_rr(request.user)
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
        if not RrPermCheck.can_create_in_zone(request.user, zone):
           raise PermissionDenied('rr create unauthorized for this zone')
        if not RrPermCheck.can_create_when_name_exist(request.user, name, type):
           raise PermissionDenied( "rr create unauthorized: name or type invalid by rule")
        if not RrPermCheck.can_create_by_rule(request.user, name, type):
           raise PermissionDenied("rr create unauthorized: rr with same name and type already exists and is not updatable by user")

        # Check if CNAME and name already exists in zone
        if type == "CNAME":
            if Rr.objects.filter(name=name, zone=zone).exists():
                raise ValidationException(detail=f"Can't create CNAME '{name}' because name already exist")
        # Check if name already exists in zone as CNAME
        if Rr.objects.filter(name=name, zone=zone, type="CNAME").exists():
            raise ValidationException(detail=f"Can't create '{name}' because CNAME with same name already exist")
 
        serializer.save()

        # FIXME: create permission object based on group of preferences

        return Response(serializer.data, status=status.HTTP_201_CREATED)

