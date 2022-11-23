from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

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
    BazarLog
)
# from authentication.serializers import UserProductSerializer


class CategoryProductSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Product
        fields = ('id', 'title')


class ProductCategorySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Category
        fields = ('id', 'title')


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class CategoryAttributSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryAttribute
        fields = '__all__'


class AttributDetailsSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    def get_value(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = AttributDetails
        fields = '__all__'


class ProductAttributSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribut
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    childs = SubCategorySerializer(many=True)
    category_attrs = CategoryAttributSerializer(many=True)
    products = CategoryProductSerializer(many=True)
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Category
        fields = '__all__'


class ProductOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    def validate(self, data):
        product = Product.objects.filter(pk=data.get("product")).first()
        quantity = data.get("quantity")
        request_type = data.get('request_type')
        if request_type == 'd' and (quantity < product.amount):
            raise ValidationError(f"you can't order more then {product.amount} of this product")
        return data

    # def create(self, validated_data):
    #     product = get_object_or_404(Product, id=validated_data.get('product'))
    #     request_type = validated_data.get('request_type')
    #     quantity = validated_data.get('quantity')
    #     if request_type == 'd':

    class Meta:
        model = ProductOrder
        fields = '__all__'


class BazarProductOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, instance):
        return instance.product.price

    def create(self, validated_data):
        instance = super(BazarProductOrderSerializer, self).create(validated_data)
        BazarLog.objects.create(by=instance.order.user, product=instance.product)

    class Meta:
        model = ProductOrder
        exclude = ['quantity']


class ProductSerializer(serializers.ModelSerializer):
    # user = UserProductSerializer()
    category = ProductCategorySerializer()
    attrs = ProductAttributSerializer(many=True)
    product_orders = ProductOrderSerializer(many=True)
    media = MediaSerializer(many=True)
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    def get_description(self, instance):
        return {
            "en": instance.description_en,
            "ar": instance.description_ar
        }

    class Meta:
        model = Product
        fields = (
            'id', 'user', 'category', 'title', 'description', 'image', 'price', 'min_price',
            'current_price',
            'increase_amount',
            'slug',
            'attrs',
            'product_orders',
            'media',
            'active',
        )


class AttributSerializer(serializers.ModelSerializer):
    values = AttributDetailsSerializer(many=True)
    category_attrs = CategoryAttributSerializer(many=True)
    product_attrs = ProductAttributSerializer(many=True)
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Attribut
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField(read_only=True)
    product_orders = ProductOrderSerializer(many=True)

    def get_total_cost(self, instance):
        return sum([elment.price for elment in instance.product_orders.all()])

    def create(self, validated_data):
        product_orders = validated_data.pop('product_orders')
        instance = super(OrderSerializer, self).create(validated_data)
        for product_order in product_orders:
            new_pd = ProductOrder(**product_order)
            new_pd.order = instance
            new_pd.save()
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
    orders = OrderSerializer(many=True)
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = ShippingCompany
        fields = '__all__'


class AddressCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = ('id', 'name', 'phone')
