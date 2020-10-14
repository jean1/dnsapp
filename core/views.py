from django.db.models.query import QuerySet
from rest_framework import viewsets, permissions, status 
from rest_framework.decorators import action
from core.models import Namespace, Zone, Rr, Zonerule
from core.serializers import NamespaceSerializer, ZoneSerializer, RrSerializer
from core.permissions import HasAccess, RrValidNameOrType
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
    filterset_fields = ['namespace']
    def list(self, request):
        queryset = get_objects_for_user(self.request.user, 'core.access_zone')
        serializer =  ZoneSerializer(queryset, many=True)
        return Response(serializer.data)
            
class RrViewSet(viewsets.ModelViewSet):
    queryset = Rr.objects.all()
    serializer_class = RrSerializer
    permission_classes = [HasAccess, RrValidNameOrType]
    filterset_fields = ['zone']

    def list(self, request):
        queryset = get_objects_for_user(self.request.user, 'core.access_rr')
        serializer = RrSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # FIXME: create permission object based on group of preferences
        # group = ?????
        # assign_perm(...) 
        pass
