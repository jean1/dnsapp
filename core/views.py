from django.db.models.query import QuerySet
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from core.models import Namespace, Zone, Rr
from core.serializers import NamespaceSerializer, ZoneSerializer, RrSerializer
from core.permissions import HasAccess
from guardian.shortcuts import get_objects_for_user
from rest_framework.response import Response

class NamespaceViewSet(viewsets.ModelViewSet):
    serializer_class = NamespaceSerializer
    permission_classes = [HasAccess]
    queryset = Namespace.objects.all()
    
    def list(self, request):
        queryset = get_objects_for_user(self.request.user, 'core.access_namespace')
        serializer = NamespaceSerializer(queryset, many=True)
        return Response(serializer.data)
        
class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer
    permission_classes = [HasAccess]
    queryset = Zone.objects.all()
    def list(self, request):
        queryset = get_objects_for_user(self.request.user, 'core.access_zone')
        serializer =  ZoneSerializer(queryset, many=True)
        return Response(serializer.data)
            
class RrViewSet(viewsets.ModelViewSet):
    queryset = Rr.objects.all()
    serializer_class = RrSerializer
    permission_classes = [HasAccess]
    def list(self, request):
        queryset = get_objects_for_user(self.request.user, 'core.access_rr')
        z = self.request.query_params.get('z', None)
        queryset = queryset.filter(zone_id=z)
        serializer = RrSerializer(queryset, many=True)
        return Response(serializer.data)
