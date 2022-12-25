from random import choices

from django.db.migrations import serializer
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from location.models import Address, City
from .models import Phone, WalletLog
from store.models import Product
from .models import User, Wallet, Review, WishList
from phonenumber_field.validators import validate_international_phonenumber


class ReviewUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')


class UserPhonerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('phone', 'type')


class WalletSubUserSerializer(serializers.ModelSerializer):
    phones = UserPhonerSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phones')


class WishListSerializer(serializers.ModelSerializer):
    objects = serializers.ListField(write_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)

    class Meta:
        model = WishList
        fields = ('id', 'product', 'objects')


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    createdat = serializers.DateTimeField(read_only=True)
    product_current = serializers.SerializerMethodField(read_only=True)

    def get_product_current(self, instance):
        return instance.product.title

    def create(self, validated_data):
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )
        return super(ReviewSerializer, self).create(validated_data)

    class Meta:
        model = Review
        fields = ('id', 'message', 'product', 'user', 'rate', 'createdat', 'product_current')


class AddressSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    address = serializers.CharField(max_length=255)


class PhoneSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        try:
            validate_international_phonenumber(value)
            return value
        except ValidationError:
            raise ValidationError('please enter a valid phone number')

    class Meta:
        model = Phone
        fields = ('phone', 'type')


class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'message', 'product')


class WalletLogSerializer(serializers.ModelSerializer):
    user = WalletSubUserSerializer(read_only=True)

    class Meta:
        model = WalletLog
        fields = ('id', 'user', 'created', 'withdraw', 'deposite')


class WalletSerializer(serializers.ModelSerializer):
    logs = WalletLogSerializer(read_only=True, many=True)

    def update(self, instance, validated_data):
        old_amount = instance.amount
        new_amount = validated_data.get('amount')
        instance = super(WalletSerializer, self).update(instance, validated_data)
        if new_amount >= old_amount:
            withdraw = new_amount - old_amount
            WalletLog.objects.create(wallet=instance, withdraw=str(withdraw))
        else:
            deposit = old_amount - new_amount
            WalletLog.objects.create(wallet=instance, deposite=str(deposit))
        return instance

    class Meta:
        model = Wallet
        fields = ('id', 'amount', 'logs')


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


class UserCreationSerializer(UserCreateSerializer):
    phones = UserPhonerSerializer(many=True)
    addresses = UserAddressSerializer(many=True)
    avatar = Base64ImageField(required=False)
    wallet = WalletSerializer(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.BooleanField(write_only=True, required=False)
    reviews = UserReviewSerializer(many=True, read_only=True)
    wishlist = WishListSerializer(many=True, read_only=True)
    user_role = serializers.CharField(max_length=10, write_only=True, required=True)

    def get_role(self, instance):
        return instance.role

    def validate(self, attrs):
        required_role = attrs.get('user_role')
        if required_role not in ['admin', 'superuser', 'normal']:
            raise ValidationError('please enter a valid user type to create !')

        if not attrs.get('phones') or len(attrs.get('phones')) == 0:
            raise ValidationError('please enter at least one valid phone number !')

        if not attrs.get('addresses') or len(attrs.get('addresses')) == 0:
            raise ValidationError('please enter at least one valid address !')
        if (required_role in ['admin', 'superuser'] or attrs.get('is_active')) \
                and not self.context['request'].user.is_superuser:
            raise ValidationError({"User type": "You dont have permession to create this type of users !"})

        return attrs

    def create(self, validated_data):
        phones = validated_data.pop('phones')
        addresses = validated_data.pop('addresses')
        user_role = validated_data.pop('user_role', 'normal')
        is_superuser = False
        is_staff = False
        if user_role == 'superuser':
            is_superuser = True
            is_staff = True
        elif user_role == 'admin':
            is_staff = True
        validated_data.update(
            {
                'is_staff': is_staff,
                'is_superuser': is_superuser
            }
        )
        instance = super(UserCreationSerializer, self).create(validated_data)
        for phone in phones:
            Phone.objects.create(user=instance, **phone)
        for location in addresses:
            location, create = Address.objects.get_or_create(user=instance, **location)
            instance.addresses.add(location)
        Wallet.objects.create(user=instance, amount=0)
        instance.save()
        return instance

    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username',
                  'password',
                  'avatar',
                  'user_role',
                  'wallet',
                  'reviews',
                  'is_active',
                  'gender',
                  'role',
                  'wishlist',
                  'phones',
                  'addresses')


class UserExtendedSerializer(UserSerializer):
    phones = PhoneSerializer(many=True)
    addresses = AddressSerializer(many=True)
    avatar = Base64ImageField(required=False)
    email = serializers.EmailField(read_only=True)
    reviews = UserReviewSerializer(many=True, read_only=True)
    wishlist = WishListSerializer(many=True, read_only=True)
    wallet = WalletSerializer(read_only=True)
    user_role = serializers.CharField(write_only=True, required=False)
    gender = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs.get('user_role') and attrs.get('user_role') not in ['admin', 'superuser', 'normal']:
            raise ValidationError({"Invalid types": "You  have entered invalid type of users !"})
        if attrs.get('user_role') and not self.context['request'].user.is_superuser:
            raise ValidationError({"User type": "You dont have permession to create this type of users !"})
        return attrs

    def update(self, instance, validated_data):
        user = self.context['request'].user
        phones = validated_data.pop('phones', None)
        addresses = validated_data.pop('addresses', None)
        username = validated_data.pop('username', None)
        user_role = validated_data.pop('user_role', 'normal')
        if User.objects.filter(username=username).exclude(pk=user.pk):
            raise ValidationError({"User exist": "user with this name already exists!"})

        is_superuser = False
        is_staff = False
        if user_role == 'superuser':
            is_superuser = True
            is_staff = True
        elif user_role == 'admin':
            is_staff = True
        validated_data.update(
            {
                'is_staff': is_staff,
                'is_superuser': is_superuser
            }
        )

        if phones:
            instance.phones.all().delete()
            for phone in phones:
                obj, created = Phone.objects.get_or_create(user=instance, **phone)
                obj.phone = phone.get('phone', obj.phone)
                obj.type = phone.get('type', obj.phone)
                obj.save()
                instance.phones.add(obj)
                instance.save()
        if addresses:
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
                  'user_role',
                  'wallet',
                  'reviews',
                  'wishlist',
                  'phones',
                  'is_active',
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


class SubUserSerializer(ModelSerializer):
    user = WalletSubUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'message', 'product', 'user')
