from rest_framework import serializers
from .models import (
    Address,
    City,
    Governorate,
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'user', 'address', 'city')


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'title', 'user', 'governorate')


class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Governorate
        fields = ('id', 'code', 'title')
