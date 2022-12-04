from rest_framework import serializers
#
# from authentication.serializers import UserAddressSerializer
from store.serializers import ShippingCompanySerializer, AddressCompanySerializer
from .models import (
    Address,
    City,
    Governorate,
)


class AddressSerializer(serializers.ModelSerializer):
    shipping_companys = AddressCompanySerializer(many=True)

    # user = UserAddressSerializer()

    class Meta:
        model = Address
        fields = ('id', 'user', 'address', 'city', 'shipping_companys')


class CitySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = City
        fields = ('id', 'title', 'governorate')


class GovernorateSerializer(serializers.ModelSerializer):
    governorate_title = serializers.SerializerMethodField()
    title_en = serializers.CharField(write_only=True)
    title_ar = serializers.CharField(write_only=True)
    cities = CitySerializer(many=True)

    def get_governorate_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Governorate
        fields = ('id', 'code', 'governorate_title',
                  'title_en',
                  'title_ar',
                  'cities',

                  )
