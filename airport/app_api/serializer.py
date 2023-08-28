from rest_framework import serializers

from app_core.models import Airport


class AirportSerializer(serializers.ModelSerializer):

    class Meta:

        model = Airport
        fields = '__all__'
