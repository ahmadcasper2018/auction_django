from rest_framework import serializers

from store.serializers import ShippingCompanySerializer
from .models import (
    Address,
    City,
    Governorate,
)


class AddressSerializer(serializers.ModelSerializer):
    shipping_companys = ShippingCompanySerializer(many=True)

    class Meta:
        model = Address
        fields = ('id', 'user', 'address', 'city', 'shipping_companys')


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'title', 'user', 'governorate')


class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Governorate
        fields = ('id', 'code', 'title')
