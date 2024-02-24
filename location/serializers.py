from rest_framework import serializers

from location.models import Nationality, Location


class NationalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nationality
        fields = ("nationality",)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("city", "country")
