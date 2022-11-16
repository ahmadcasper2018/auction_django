from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer


class UserCreationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username', 'password', 'avatar', 'gender')


class UserExtendedSerializer(UserSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'username', 'avatar', 'gender')
