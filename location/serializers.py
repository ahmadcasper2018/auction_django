from rest_framework import serializers
#
# from authentication.serializers import UserAddressSerializer
from store.serializers import ShippingCompanySerializer, AddressCompanySerializer
from .models import (
    Address,
    City,
    Governorate,
)
from store.models import ShippingCompany


class SubCompanySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name_current = serializers.CharField(read_only=True, source='title')
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        return {
            'en': instance.name_en,
            'ar': instance.name_ar

        }


class AddressSerializer(serializers.ModelSerializer):
    shipping_companys = SubCompanySerializer(read_only=True, many=True)
    address = serializers.SerializerMethodField()
    address_currnet = serializers.CharField(read_only=True, source='address')
    address_en = serializers.CharField(write_only=True)
    address_ar = serializers.CharField(write_only=True)

    def get_address(self, instance):
        return {
            'en': instance.address_en,
            'ar': instance.address_ar,
        }

    # user = UserAddressSerializer()

    class Meta:
        model = Address
        fields = ('id', 'user', 'address', 'city', 'shipping_companys',
                  'address_currnet',
                  'address_en', 'address_ar',)


class CitySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    title_currnet = serializers.CharField(read_only=True, source='title')
    title_en = serializers.CharField(write_only=True)
    title_ar = serializers.CharField(write_only=True)

    def get_title(self, instance):
        return {
            'en': instance.title_en,
            'ar': instance.title_ar,
        }

    class Meta:
        model = City
        fields = ('id', 'title_currnet', 'title', 'title_en', 'title_ar', 'governorate',
                  'title_en', 'title_ar')


class CityInnerSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    title_currnet = serializers.CharField(read_only=True, source='title')

    def get_title(self, instance):
        return {
            'en': instance.title_en,
            'ar': instance.title_ar
        }

    class Meta:
        model = City
        fields = ('id', 'title', 'title_currnet')


class GovernorateSerializer(serializers.ModelSerializer):
    cities = CityInnerSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    title_currnet = serializers.CharField(read_only=True, source='title')
    title_en = serializers.CharField(write_only=True)
    title_ar = serializers.CharField(write_only=True)

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Governorate
        fields = ('id', 'code',
                  'title_en',
                  'title_ar',
                  'cities',
                  'title_currnet',
                  'title'

                  )
