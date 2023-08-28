from rest_framework.routers import DefaultRouter
from django.urls import path
from app_api.viewsets import AirportViewSet 
from app_api.views import FlightView


router = DefaultRouter()
router.register('airports', AirportViewSet, basename="airports"),

urlpatterns = [
    path("flight", FlightView.as_view(), name="flight"),
]

urlpatterns += router.urls
