from rest_framework import serializers

from .models import (
    Product,
    Category,
    Order,
    ShippingCompany,
    Media,
    AttributDetails,
    ProductOrder,
    ProductAttribut,
)
from account.serializers import UserSerializer


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

    class Meta:
        model = Category
        fields = '__all__'


class ProductOrderSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    class Meta:
        model = ProductOrder
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    category = CategorySerializer()
    attrs = ProductAttributSerializer(many=True)
    product_orders = ProductOrderSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            'id', 'user', 'category', 'title', 'title_ar', 'description', 'image', 'price', 'min_price',
            'current_price',
            'increase_amount',
            'slug',
            'attrs',
        )


class OrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()
    product_orders = ProductOrderSerializer(many=True)

    def get_total_cost(self, instance):
        return sum([elment.price for elment in instance.product_orders.all()])

    class Meta:
        model = Order
        fields = '__all__'


class ShippingCompanySerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)

    class Meta:
        model = ShippingCompany
        fields = '__all__'
