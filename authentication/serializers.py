from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.exceptions import ValidationError

from .models import Phone
from store.models import Product


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

    def validate(self, attrs):
        if not attrs.get('phones') or len(attrs.get('phones')) == 0:
            raise ValidationError('please enter at least one valid phone number !')
        return attrs

    def create(self, validated_data):
        phones = validated_data.pop('phones')
        instance = super(UserCreationSerializer, self).create(validated_data)
        for phone in phones:
            Phone.objects.create(user=instance, **phone)
        return instance

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username', 'password', 'avatar', 'gender', 'phones')


class UserExtendedSerializer(UserSerializer):
    products = UserProductSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'username', 'avatar', 'gender', 'is_active', 'role', 'products')


class PhoneNumberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Phone
        fields = ('id', 'user', 'phone', 'type')
