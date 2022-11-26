from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from location.models import City, Address
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


# from authentication.serializers import UserProductSerializer


class CompanyAddressSerializer(serializers.Serializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    address = serializers.CharField(max_length=255)


class CategoryProductSerializer(serializers.ModelSerializer):
    # title = serializers.SerializerMethodField()
    id = serializers.IntegerField()

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

    class Meta:
        model = Product
        fields = ('id', 'title', 'title_en', 'title_ar')


class ProductCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    title_en = serializers.CharField(max_length=255)
    title_ar = serializers.CharField(max_length=255)
    # title = serializers.SerializerMethodField()
    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }




class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class CategoryAttributSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryAttribute
        fields = '__all__'


class AttributDetailsSerializer(serializers.ModelSerializer):
    # value = serializers.SerializerMethodField()

    # def get_value(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

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

    # title = serializers.SerializerMethodField()

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

    class Meta:
        model = Category
        fields = '__all__'


class ProductOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    price = serializers.SerializerMethodField(read_only=True)
    directed_bazar = serializers.BooleanField()

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    def validate(self, data):
        product = Product.objects.filter(pk=data.get("product")).first()
        quantity = data.get("quantity")
        category_title = product.category.parent_title
        directed_mozaeda = data.get('directed_mozaeda')
        if category_title in ['direct', 'bazar']:
            if not quantity:
                raise ValidationError(f"please enter the amount of products you want to purchase")
            elif quantity < product.amount:
                raise ValidationError(f"you can't order more then {product.amount} of this product")
        elif category_title != 'mozaeda':
            raise ValidationError(f"there no order logic for this product as it's not from the three main categories")

        return data

    class Meta:
        model = ProductOrder
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # user = UserProductSerializer()
    category = ProductCategorySerializer()
    attrs = ProductAttributSerializer(many=True, required=False)
    product_orders = ProductOrderSerializer(many=True, required=False)
    media = MediaSerializer(many=True, required=False)
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
        category = validated_data.pop('category')
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )
        instance = super(ProductSerializer, self).create(validated_data)
        category_obj = get_object_or_404(Category, pk=int(category['id']))
        instance.category = category_obj
        instance.save()
        return instance

    class Meta:
        model = Product
        fields = (
            'id', 'user', 'category', 'title', 'description', 'image', 'price', 'min_price',
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
    category_attrs = CategoryAttributSerializer(many=True)
    product_attrs = ProductAttributSerializer(many=True)

    # title = serializers.SerializerMethodField()

    # def get_title(self, instance):
    #     return {
    #         "en": instance.title_en,
    #         "ar": instance.title_ar
    #     }

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
        directed_mozaeda = validated_data.pop('directed_mozaeda')
        instance = super(OrderSerializer, self).create(validated_data)
        for product_order in product_orders:
            serializer = ProductOrderSerializer(product_order)
            serializer.is_valid(raise_exception=True)
            new_pd = serializer.save()
            new_pd.order = instance
            if new_pd.product.category.parent_title == 'mozaeda':
                new_pd.product.current_price = new_pd.product.current_price + new_pd.product.increase_amount
                instance.save()
            elif new_pd.product.category.parent_title in ['bazar', 'direct']:
                new_pd.product.amount = new_pd.product.amount - new_pd.product.quantity
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
    orders = OrderSerializer(many=True)
    # name = serializers.SerializerMethodField()
    address = CompanyAddressSerializer()

    # def get_name(self, instance):
    #     return {
    #         "en": instance.name_en,
    #         "ar": instance.name_ar
    #     }

    def create(self, validated_data):
        address = validated_data.pop('address')
        instance = super(ShippingCompanySerializer, self).create(validated_data)
        location, create = Address.objects.get_or_create(**address)
        instance.address = location
        return instance

    class Meta:
        model = ShippingCompany
        fields = '__all__'


class AddressCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompany
        fields = ('id', 'name', 'phone')
