from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from app_api.serializer import AirportSerializer
from app_core.models import Airport


class AirportViewSet(ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()

    def list(self, request):
        queryset = Airport.objects.all()
        serializer = AirportSerializer(queryset, many=True)
        return Response(serializer.data)
