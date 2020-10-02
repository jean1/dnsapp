from rest_framework import viewsets, permissions
from core.models import Namespace, Zone, Rr
from core.serializers import NamespaceSerializer, ZoneSerializer, RrSerializer
from core.permissions import HasAccess

class NamespaceViewSet(viewsets.ModelViewSet):
    queryset = Namespace.objects.all()
    serializer_class = NamespaceSerializer
    permission_classes = [HasAccess]

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [HasAccess]

class RrViewSet(viewsets.ModelViewSet):
    queryset = Rr.objects.all()
    serializer_class = RrSerializer
    permission_classes = [HasAccess]
