from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views

# Create a router and register our viewsets with it.
router = DefaultRouter()

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
urlpatterns += [
    path('namespace/', views.NamespaceListOrCreate.as_view()),
    path('namespace/<int:pk>/', views.NamespaceDetail.as_view()),
    path('zone/', views.ZoneListOrCreate.as_view()),
    path('zone/<int:pk>/', views.ZoneDetail.as_view()),
    path('zone/<int:pk>/rr/', views.ZoneRrList.as_view()),
    path('rr/', views.RrListOrCreate.as_view()),
    path('rr/<int:pk>/', views.RrDetail.as_view()),
]
