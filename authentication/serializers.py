from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework_simplejwt.tokens import RefreshToken

from location.models import Address, City
from .models import Phone
from store.models import Product
from .models import User


class UserAddressSerializer(serializers.Serializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    address = serializers.CharField(max_length=255)


class UserProductSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Product
        fields = ('id', 'title')


class UserPhonerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('phone', 'type')


class UserCreationSerializer(UserCreateSerializer):
    phones = UserPhonerSerializer(many=True)
    addresses = UserAddressSerializer(many=True)
    avatar = Base64ImageField(required=False)

    def validate(self, attrs):
        if not attrs.get('phones') or len(attrs.get('phones')) == 0:
            raise ValidationError('please enter at least one valid phone number !')

        if not attrs.get('addresses') or len(attrs.get('addresses')) == 0:
            raise ValidationError('please enter at least one valid address !')
        return attrs

    def create(self, validated_data):
        phones = validated_data.pop('phones')
        addresses = validated_data.pop('addresses')
        instance = super(UserCreationSerializer, self).create(validated_data)
        for phone in phones:
            Phone.objects.create(user=instance, **phone)
        for location in addresses:
            location, create = Address.objects.get_or_create(user=instance, **location)
            instance.addresses.add(location)
        return instance

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username',
                  'password',
                  'avatar',
                  'gender',
                  'phones',
                  'addresses')


class UserExtendedSerializer(UserSerializer):
    products = UserProductSerializer(many=True)
    phones = UserPhonerSerializer(many=True)
    addresses = UserAddressSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'username', 'avatar',
                  'gender',
                  'is_active',
                  'role',
                  'products',
                  'phones',
                  'addresses')


class PhoneNumberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Phone
        fields = ('id', 'user', 'phone', 'type')


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
