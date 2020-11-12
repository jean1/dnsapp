from django.db.models.query import QuerySet
from rest_framework import viewsets, permissions, status 
from rest_framework.decorators import action
from core.models import Namespace, Zone, Rr, Zonerule, PermNamespace, PermZone, PermRr
from core.serializers import NamespaceSerializer, ZoneSerializer, RrSerializer
from core.permissions import NamespaceAccess, ZoneCreate, ZoneAccess, RrAccess, RrValidNameOrType
from rest_framework.response import Response

class NamespaceViewSet(viewsets.ModelViewSet):
    serializer_class = NamespaceSerializer
    permission_classes = [NamespaceAccess]
    queryset = Namespace.objects.all()
    
    def list(self, request):
        queryset = NamespaceAccess.allowed_namespaces(request.user)
        serializer = NamespaceSerializer(queryset, many=True)
        return Response(serializer.data)
        
class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer
    permission_classes = [ZoneAccess, ZoneCreate]
    queryset = Zone.objects.all()
    filterset_fields = ['namespace']
    def list(self, request):
        queryset = allowed_zone(self.request.user)
        serializer =  ZoneSerializer(queryset, many=True)
        return Response(serializer.data)
    def perform_create(self, serializer):
        # FIXME: add permission to created objects
        pass
            
class RrViewSet(viewsets.ModelViewSet):
    queryset = Rr.objects.all()
    serializer_class = RrSerializer
    permission_classes = [RrAccess, RrValidNameOrType]
    # FIXME: Add CreateRrInZone permission class
    filterset_fields = ['zone']

    def list(self, request):
        queryset = get_objects_for_user(self.request.user, 'core.access_rr')
        serializer = RrSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        name = serializer.validated_data['name']
        zone = serializer.validated_data['zone']

        # Check if CNAME and name already exists in zone
        if type == "CNAME":
            if Rr.objects.filter(name=name, zone=zone).exists():
                raise ValidationException(detail=f"Can't create CNAME '{name}' because name already exist")
        # Check if name already exists in zone as CNAME
        if Rr.objects.filter(name=name, zone=zone, type="CNAME").exists():
            raise ValidationException(detail=f"Can't create '{name}' because CNAME with same name already exist")
 
        # FIXME: create permission object based on group of preferences
