from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'namespace', views.NamespaceViewSet)
router.register(r'zone', views.ZoneViewSet)
router.register(r'rr', views.RrViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
