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

    class Meta:
        model = City
        fields = ('id', 'title_en', 'title_ar', 'governorate')


class CityInnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'title_en', 'title_ar')


class GovernorateSerializer(serializers.ModelSerializer):
    # governorate_title = serializers.SerializerMethodField()
    cities = CityInnerSerializer(many=True)

    # def get_governorate_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }
    def create(self, validated_data):
        cities = validated_data.pop('cities')
        instance = super(GovernorateSerializer, self).create(validated_data)
        for city in cities:
            serilizer = CityInnerSerializer(data=city)
            serilizer.is_valid(raise_exception=True)
            obj = serilizer.save(governorate=instance)
            obj.save()
        return instance

    class Meta:
        model = Governorate
        fields = ('id', 'code',
                  'title_en',
                  'title_ar',
                  'cities',

                  )
