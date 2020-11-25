from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'namespace', views.NamespaceViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
urlpatterns += [
    path('zone/', views.ZoneListOrCreate.as_view()),
    path('zone/<int:pk>/', views.ZoneDetail.as_view()),
    path('rr/', views.RrListOrCreate.as_view()),
    path('rr/<int:pk>/', views.RrDetail.as_view()),
]
