import phone as phone
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import Phone
from .models import User


class UserCreationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username', 'password', 'avatar', 'gender')


class UserExtendedSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'username', 'avatar', 'gender')


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('id', 'user', 'phone', 'type')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
