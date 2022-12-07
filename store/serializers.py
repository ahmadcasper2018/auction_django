from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from location.models import City, Address, Governorate
from .models import (
    Product,
    Category,
    Order,
    ShippingCompany,
    Media,
    CategoryAttribute,
    AttributDetails,
    ProductOrder,
    ProductAttribut,
    Attribut,
    OrderLog,

)

from drf_extra_fields.fields import Base64ImageField


# from authentication.serializers import UserProductSerializer


def validate_product_order(data):
    product = data.get("product")
    quantity = data.get("quantity")
    category_title = product.category.parent_title
    # directed_mozaeda = data.get('directed_mozaeda')
    if category_title in ['direct', 'bazar']:
        if not quantity:
            raise ValidationError(f"please enter the amount of products you want to purchase")
        elif quantity > product.amount:
            raise ValidationError(f"you can't order more then {product.amount} of this product")
    elif category_title != 'mozaeda':
        raise ValidationError(f"there no order logic for this product as it's not from the three main categories")


class AddressCompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'city', 'address')


class CategoryProductSerializer(serializers.ModelSerializer):
    # title = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    image = Base64ImageField(required=False)

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

    class Meta:
        model = Product
        fields = ('id', 'title', 'title_en', 'title_ar', 'image')


class ProductCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    # title = serializers.SerializerMethodField()
    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }


class MediaSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, instance):
        return instance.type

    class Meta:
        model = Media
        fields = ('id', 'file', 'type')


class CategoryAttributSerializer(serializers.ModelSerializer):
    attribut_title = serializers.SerializerMethodField(read_only=True)
    attribut_value = serializers.SerializerMethodField(read_only=True)

    def get_attribut_title(self, instance):
        return instance.attribut.title

    def get_attribut_value(self, instance):
        return instance.attribut.values.all().values('value')

    class Meta:
        model = CategoryAttribute
        fields = ('id', 'attribut', 'attribut_title', 'attribut_value')


class AttributDetailsSerializer(serializers.ModelSerializer):
    # value = serializers.SerializerMethodField()
    id = serializers.IntegerField(required=False)

    # def get_value(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

    class Meta:
        model = AttributDetails
        fields = ('id', 'value', 'value_en', 'value_ar')


class ProductAttributSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribut
        fields = '__all__'


class ProductAttributSubSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField(read_only=True)
    value = serializers.SerializerMethodField(read_only=True)
    value_ar = serializers.CharField(write_only=True)
    value_en = serializers.CharField(write_only=True)

    def get_value(self, instance):
        return {
            "en": instance.value_en,
            "ar": instance.value_ar
        }

    def get_title(self, instance):
        return {
            "en": instance.attribut.title_en,
            "ar": instance.attribut.title_ar
        }

    class Meta:
        model = ProductAttribut
        fields = ('id', 'attribut', 'value_en', 'value_ar',
                  'title',
                  'value',)


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    childs = SubCategorySerializer(many=True, read_only=True)
    category_attrs = CategoryAttributSerializer(many=True, required=False)
    products = CategoryProductSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)

    # title = serializers.SerializerMethodField()

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

    def create(self, validated_data):
        category_attrs = validated_data.pop('category_attrs')
        instance = super(CategorySerializer, self).create(validated_data)
        if category_attrs:
            for attr in category_attrs:
                obj, created = CategoryAttribute.objects.get_or_create(**attr)
                obj.category = instance
                obj.save()
                instance.category_attrs.add(obj)
            instance.save()
        return instance

    class Meta:
        model = Category
        fields = '__all__'


class ProductOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    price = serializers.SerializerMethodField(read_only=True)

    # product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    # directed_bazar = serializers.BooleanField()

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    class Meta:
        model = ProductOrder
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # user = UserProductSerializer()
    category = ProductCategorySerializer()
    attrs = ProductAttributSubSerializer(many=True, required=False)
    product_orders = ProductOrderSerializer(many=True, read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)
    # title = serializers.SerializerMethodField()
    # description = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }
    #
    # def get_description(self, instance):
    #     return {
    #         "en": instance.description_en,
    #         "ar": instance.description_ar
    #     }

    def create(self, validated_data):
        category = validated_data.pop('category', None)
        attrs = validated_data.pop('attrs', None)

        media_files = self.context['request'].data[0].get('media_files')
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )
        instance = super(ProductSerializer, self).create(validated_data)
        category_obj = get_object_or_404(Category, pk=int(category['id']))
        instance.category = category_obj
        if attrs:
            for attr in attrs:
                obj, created = ProductAttribut.objects.get_or_create(product=instance, **attr)
                obj.product = instance
                obj.save()
                instance.attrs.add(obj)
        if media_files:
            for file_id in media_files:
                media_obj = get_object_or_404(Media, pk=int(file_id))
                instance.media.add(media_obj)
                instance.save()

        instance.save()
        return instance

    def update(self, instance, validated_data):
        category = validated_data.pop('category', None)
        attrs = validated_data.pop('attrs', None)
        media_files = self.context['request'].data.get('media_files')
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )
        instance = super(ProductSerializer, self).update(instance, validated_data)
        category_obj = get_object_or_404(Category, pk=int(category['id']))
        instance.category = category_obj
        if attrs:
            instance.attrs.clear()
            for attr in attrs:
                obj, created = ProductAttribut.objects.get_or_create(product=instance, **attr)
                obj.product = instance
                obj.save()
                instance.attrs.add(obj)
        if media_files:
            instance.media.clear()
            for file_id in media_files:
                media_obj = get_object_or_404(Media, pk=int(file_id))
                instance.media.add(media_obj)
                instance.save()
        instance.save()
        return instance

    class Meta:
        model = Product
        fields = (
            'id', 'user', 'category', 'title', 'title_en', 'title_ar', 'description', 'image', 'price', 'min_price',
            'current_price',
            'increase_amount',
            'attrs',
            'product_orders',
            'media',
            'active',
            'amount',
        )


class AttributSerializer(serializers.ModelSerializer):
    values = AttributDetailsSerializer(many=True)

    # title = serializers.SerializerMethodField()

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

    def create(self, validated_data):
        values = validated_data.pop('values')
        instance = super(AttributSerializer, self).create(validated_data)
        for value in values:
            obj, created = AttributDetails.objects.get_or_create(attribut=instance, **value)
            obj.attribut = instance
            obj.save()
            instance.values.add(obj)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        values = validated_data.pop('values')
        instance = super(AttributSerializer, self).update(instance, validated_data)
        for value in values:
            obj = get_object_or_404(AttributDetails, pk=int(value['id']))
            obj.value = value.get('value', obj.value)
            obj.value_en = value.get('value', obj.value_en)
            obj.value_ar = value.get('value', obj.value_ar)
            obj.save()
        return instance

    class Meta:
        model = Attribut
        fields = ('id', 'title', 'values')


class OrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField(read_only=True)
    product_orders = ProductOrderSerializer(many=True)

    def get_total_cost(self, instance):
        return sum([elment.price for elment in instance.product_orders.all()])

    def create(self, validated_data):
        product_orders = validated_data.pop('product_orders')
        directed_mozaeda = validated_data.pop('directed_mozaeda', None)
        validated_data.update({"user": self.context['request'].user})
        instance = super(OrderSerializer, self).create(validated_data)
        for product_order in product_orders:
            quantity = product_order.get('quantity')
            validate_product_order(product_order)
            new_pd = ProductOrder.objects.create(**product_order)
            new_pd.order = instance
            if new_pd.product.category.parent_title == 'mozaeda':
                new_pd.product.current_price = new_pd.product.current_price + new_pd.product.increase_amount
                instance.save()
            elif new_pd.product.category.parent_title in ['bazar', 'direct']:
                new_pd.product.amount = new_pd.product.amount - quantity
                instance.save()
            instance.product_orders.add(new_pd)
            instance.save()

        OrderLog.objects.create(order=instance, mozaeda=bool(directed_mozaeda))
        return instance

    def update(self, instance, validated_data):
        product_orders = validated_data.pop('product_orders')
        instance = super(OrderSerializer, self).update(instance, validated_data)
        for product_order in product_orders:
            item = ProductOrder.objects.get(id=product_order.pop('id'))
            item.order = product_order.get('order', item.order)
            item.product = product_order.get('product', item.product)
            item.attribut = product_order.get('attribut', item.attribut)
            item.quantity = product_order.get('quantity', item.quantity)
            item.save()
        return instance

    class Meta:
        model = Order
        fields = '__all__'


class ShippingCompanySerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    # name = serializers.SerializerMethodField()
    address = AddressCompanySerializer()

    # def get_name(self, instance):
    #     return {
    #         "en": instance.name_en,
    #         "ar": instance.name_ar
    #     }

    def create(self, validated_data):
        address = validated_data.pop('address')
        location, created = Address.objects.get_or_create(**address)
        validated_data.update({"address": location})
        instance = super(ShippingCompanySerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        address = validated_data.pop('address')
        instance.name_en = validated_data.get('name_en', instance.name_en)
        instance.name_ar = validated_data.get('name_ar', instance.name_ar)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.phone = validated_data.get('phone', instance.phone)
        location, created = Address.objects.get_or_create(**address)
        instance.address = location
        instance.save()
        return instance

    class Meta:
        model = ShippingCompany
        fields = '__all__'
