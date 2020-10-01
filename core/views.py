from rest_framework import viewsets, permissions
from core.models import Namespace
from core.serializers import NamespaceSerializer

class NamespaceViewSet(viewsets.ModelViewSet):
    queryset = Namespace.objects.all()
    serializer_class = NamespaceSerializer
    permission_classes = [permissions.IsAuthenticated]

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticated]

class RrViewSet(viewsets.ModelViewSet):
    queryset = Rr.objects.all()
    serializer_class = RrSerializer
    permission_classes = [permissions.IsAuthenticated]
