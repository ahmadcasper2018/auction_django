from django.db.migrations import serializer
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework_simplejwt.tokens import RefreshToken

from location.models import Address, City
from .models import Phone
from store.models import Product
from .models import User, Wallet, Review, WishList


class WishListSerializer(serializers.ModelSerializer):
    objects = serializers.ListField(write_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)

    class Meta:
        model = WishList
        fields = ('id', 'product', 'objects')


class ReviewSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )
        return super(ReviewSerializer, self).create(validated_data)

    class Meta:
        model = Review
        fields = ('id', 'message', 'product')


class AddressSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    address = serializers.CharField(max_length=255)


class PhoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Phone
        fields = ('id', 'phone', 'type')


class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'message', 'product')


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('id', 'amount')


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
    wallet = WalletSerializer(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    is_staff = serializers.BooleanField(write_only=True, required=False)
    is_superuser = serializers.BooleanField(write_only=True, required=False)
    reviews = UserReviewSerializer(many=True, read_only=True)
    wishlist = WishListSerializer(many=True, read_only=True)

    def get_role(self, instance):
        return instance.role

    def validate(self, attrs):
        if not attrs.get('phones') or len(attrs.get('phones')) == 0:
            raise ValidationError('please enter at least one valid phone number !')

        if not attrs.get('addresses') or len(attrs.get('addresses')) == 0:
            raise ValidationError('please enter at least one valid address !')
        if (attrs.get('is_staff') or attrs.get('is_superuser')) and not self.context['request'].user.is_superuser:
            raise ValidationError({"User type": "You dont have permession to create this type of users !"})

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
        Wallet.objects.create(user=instance, amount=0)
        return instance

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username',
                  'password',
                  'avatar',
                  'is_staff',
                  'is_superuser',
                  'wallet',
                  'reviews',
                  'gender',
                  'role',
                  'wishlist',
                  'phones',
                  'addresses')


class UserExtendedSerializer(UserSerializer):
    phones = PhoneSerializer(many=True)
    addresses = AddressSerializer(many=True)
    avatar = Base64ImageField(required=False)
    reviews = UserReviewSerializer(many=True, read_only=True)
    wishlist = WishListSerializer(many=True, read_only=True)
    wallet = WalletSerializer(read_only=True)

    def validate(self, attrs):
        if not attrs.get('phones') or len(attrs.get('phones')) == 0:
            raise ValidationError('please enter at least one valid phone number !')
        if not attrs.get('addresses') or len(attrs.get('addresses')) == 0:
            raise ValidationError('please enter at least one valid address !')
        if (attrs.get('is_staff') or attrs.get('is_superuser') or attrs.get('is_staff')) and not \
                self.context['request'].user.is_superuser:
            raise ValidationError({"User type": "You dont have permession to create this type of users !"})
        return attrs

    def update(self, instance, validated_data):
        phones = validated_data.pop('phones')
        addresses = validated_data.pop('addresses')
        instance.phones.all().delete()
        instance.addresses.all().delete()
        for phone in phones:
            obj, created = Phone.objects.get_or_create(user=instance, **phone)
            obj.phone = phone.get('phone', obj.phone)
            obj.type = phone.get('type', obj.phone)
            obj.save()
            instance.phones.add(obj)
            instance.save()

        for location in addresses:
            obj, created = Address.objects.get_or_create(user=instance, **location)
            obj.city = location.get('city', obj.city)
            obj.address = location.get('address', obj.address)
            obj.save()
            instance.addresses.add(obj)
            instance.save()
        return super(UserExtendedSerializer, self).update(instance, validated_data)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'username', 'avatar',
                  'gender',
                  'is_active',
                  'is_superuser',
                  'is_staff',
                  'wallet',
                  'reviews',
                  'wishlist',
                  'phones',
                  'role',
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


class UserDetailSerializer(serializers.ModelSerializer):
    phones = UserPhonerSerializer(many=True)
    addresses = UserAddressSerializer(many=True)
    avatar = Base64ImageField(required=False)
    reviews = UserReviewSerializer(many=True, read_only=True)
    wallet = WalletSerializer(read_only=True)
    wishlist = WishListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'avatar',
                  'gender',
                  'is_active',
                  'role',
                  'wishlist',
                  'wallet',
                  'reviews',
                  'products',
                  'phones',
                  'addresses')
