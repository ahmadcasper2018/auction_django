from django.db.models import Max
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from authentication.models import User
from authentication.serializers import SubUserSerializer
from location.models import Address
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
    Brand, SliderMedia, Slider, AuctionOrder, AttributValue, Page, ProductViewers,

)

from drf_extra_fields.fields import Base64ImageField


def handle_404(message, field):
    errors = {
        field: [f"the entered {field} is not valid"]
    }

    return {
        "message": message,
        "errors": errors
    }


# from authentication.serializers import UserProductSerializer
class AttributeValueSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    value_current = serializers.CharField(read_only=True, source='value')
    value_en = serializers.CharField(write_only=True)
    value_ar = serializers.CharField(write_only=True)

    def get_value(self, instance):
        return {
            'en': instance.value_en,
            'ar': instance.value_ar
        }

    class Meta:
        model = AttributValue
        fields = ('id', 'value', 'value_ar', 'value_en', 'value_current',)


def validate_product_order(data):
    product = data.get("product")
    quantity = data.get("quantity")
    category_title = product.product_type
    if category_title in ['bazaar', 'shops']:
        if not quantity:
            raise ValidationError(f"please enter the amount of products you want to purchase")
        elif quantity > product.amount:
            raise ValidationError(f"you can't order more then {product.amount} of this product")
    else:
        raise ValidationError(f"there no order logic for this product as it's not from the three main categories")


class BrandSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    title_current = serializers.CharField(read_only=True, source='title')
    title_en = serializers.CharField(write_only=True)
    title_ar = serializers.CharField(write_only=True)
    image = Base64ImageField(required=False)

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Brand
        fields = ('id', 'title', 'title_en', 'title_ar', 'image', 'category', 'title_current')


class AddressCompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'city', 'address')


class CategoryProductSerializer(serializers.ModelSerializer):
    title_current = serializers.CharField(read_only=True, source='title')
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)
    id = serializers.IntegerField()
    image = Base64ImageField(required=False)
    title = serializers.SerializerMethodField()

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Product
        fields = ('id', 'title', 'title_en', 'title_ar', 'image', 'title_current')


class ProductCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    brands = BrandSerializer(many=True, read_only=True)


class MediaSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, instance):
        return instance.type

    class Meta:
        model = Media
        fields = ('id', 'file', 'type', 'attributes', 'alt', 'value')


class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'file')


class SliderMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderMedia
        fields = ('id', 'file')


class SliderSerializer(serializers.ModelSerializer):
    media = SliderMediaSerializer(source='slider_media', read_only=True)
    title_current = serializers.CharField(read_only=True, source='title')
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    description_current = serializers.CharField(read_only=True, source='description')
    description_ar = serializers.CharField(write_only=True)
    description_en = serializers.CharField(write_only=True)

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

    def create(self, validated_data):
        instance = super(SliderSerializer, self).create(validated_data)
        media_file = self.context['request'].data['media_file']
        if media_file:
            media_obj = get_object_or_404(SliderMedia, pk=media_file)
            instance.slider_media = media_obj
            instance.save()
        instance.save()
        return instance

    class Meta:
        model = Slider
        fields = ('id',
                  'title',
                  'media',
                  'slider_media',
                  'title_en',
                  'slider_media',
                  'title_current',
                  'page',
                  'description_current',
                  'title_ar',
                  'description',
                  'description_ar',
                  'description_en')


class CategoryAttributSerializer(serializers.ModelSerializer):
    attribut_title = serializers.SerializerMethodField(read_only=True)
    attribut_value = serializers.SerializerMethodField(read_only=True)

    def get_attribut_title(self, instance):
        if instance.attribut:
            return instance.attribut.title
        else:
            return ''

    def get_attribut_value(self, instance):
        return instance.attribut.values.all().values('value')

    class Meta:
        model = CategoryAttribute
        fields = ('id', 'attribut', 'attribut_title', 'attribut_value')


class AttributDetailsSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(required=False)
    value_ar = serializers.CharField(write_only=True)
    value_en = serializers.CharField(write_only=True)
    value_current = serializers.CharField(read_only=True, source='value')

    def get_value(self, instance):
        return {
            "en": instance.value_en,
            "ar": instance.value_ar
        }

    class Meta:
        model = AttributDetails
        fields = ('id', 'value', 'value_en', 'value_ar', 'value_current')


class AbstractAttributDetailsSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField(read_only=True)
    id = serializers.IntegerField(required=False)
    value_current = serializers.CharField(read_only=True, source='value')
    value_ar = serializers.CharField(write_only=True)
    value_en = serializers.CharField(write_only=True)

    def get_value(self, instance):
        return {
            "en": instance.value_en,
            "ar": instance.value_ar
        }

    class Meta:
        model = AttributDetails
        fields = ('id', 'value', 'value_en', 'value_ar', 'value_current', 'attribut')


class ProductAttributSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribut
        fields = '__all__'


class ProductAttributSubSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField(read_only=True)
    values = AttributeValueSerializer(many=True, read_only=True)
    title_current = serializers.CharField(read_only=True, source='title')

    def get_title(self, instance):
        return {
            "en": instance.attribut.title_en,
            "ar": instance.attribut.title_ar
        }

    class Meta:
        model = ProductAttribut
        fields = ('id', 'attribut',
                  'title',
                  'values',
                  'title_current',)


class SubCategorySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField(read_only=True)
    title_current = serializers.CharField(read_only=True, source='title')
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    class Meta:
        model = Category
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    childs = SubCategorySerializer(many=True, read_only=True)
    category_attrs = CategoryAttributSerializer(many=True, required=False)
    products = CategoryProductSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)
    title_current = serializers.CharField(read_only=True, source='title')
    title = serializers.SerializerMethodField(required=False)
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)

    def validate(self, attrs):
        code = attrs.get('code', None)
        if code:
            if code not in [Category.AUCTION, Category.SHOP, Category.BAZAR]:
                raise ValidationError("invalid code")
            objs = Category.objects.filter(code=code)
            if len(objs) > 0:
                raise ValidationError("Category already exist !")
        return attrs

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

    @transaction.atomic
    def create(self, validated_data):
        category_attrs = validated_data.pop('category_attrs', None)
        instance = super(CategorySerializer, self).create(validated_data)
        if category_attrs:
            for attr in category_attrs:
                new_obj = CategoryAttribute.objects.create(**attr)
                new_obj.category = instance
                new_obj.save()
                instance.category_attrs.add(new_obj)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        category_attrs = validated_data.pop('category_attrs', None)
        instance = super(CategorySerializer, self).update(instance, validated_data)
        if category_attrs:
            instance.category_attrs.clear()
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
    attrs = ProductAttributSubSerializer(many=True, required=False, read_only=True)
    product_orders = ProductOrderSerializer(many=True, read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)
    address = AddressCompanySerializer()
    title = serializers.SerializerMethodField(required=False)
    title_current = serializers.CharField(read_only=True, source='title')
    description_current = serializers.CharField(read_only=True, source='description')
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_ar = serializers.CharField(write_only=True)
    description_en = serializers.CharField(write_only=True)
    reviews = SubUserSerializer(many=True, read_only=True)
    discount = serializers.DecimalField(max_digits=10, decimal_places=3, required=False)
    tags = serializers.SerializerMethodField()

    def get_tags(self, instance):
        return instance.tags_show

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, instance):
        return instance.product_type

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

    @transaction.atomic
    def create(self, validated_data):
        category = validated_data.pop('category', None)
        if not category:
            raise ValidationError('you have to enter a category')
        attrs = self.context['request'].data.get('attrs', None)
        media_files = self.context['request'].data.get('media_files')
        address = validated_data.pop('address', None)
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )

        category_obj = Category.objects.filter(pk=category['id']).first()
        if not category_obj:
            raise ValidationError(handle_404('invalid input', 'Category'))

        instance = super(ProductSerializer, self).create(validated_data)
        instance.category = category_obj
        if attrs:
            for attr in attrs:
                attribut_id = attr.get('attribute')
                attribute = Attribut.objects.filter(pk=attribut_id).first()
                if not attribute:
                    raise ValidationError(handle_404('invalid input', 'attribute'))
                values = attr.get('values')
                new_product_attribute = ProductAttribut.objects.create(
                    attribut=attribute,
                    product=instance
                )
                values_obs = AttributValue.objects.filter(pk__in=values)
                if not values_obs:
                    raise ValidationError(handle_404('invalid input', 'values'))
                for value in values_obs:
                    new_product_attribute.values.add(value)
                new_product_attribute.save()

        if media_files:
            for file_id in media_files:
                media_obj = Media.objects.filter(pk=int(file_id)).first()
                if not media_obj:
                    raise ValidationError(handle_404('invalid input', 'media'))
                instance.media.add(media_obj)
                instance.save()
        if address:
            obj = Address.objects.filter(**address).first()
            if not obj:
                obj = Address.objects.create(**address)
                instance.address = obj
                instance.save()
        instance.address = obj
        ProductViewers.objects.create(
            product=instance
        )
        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        category = validated_data.pop('category', None)
        attrs = validated_data.pop('attrs', None)
        media_files = self.context['request'].data.get('media_files')
        address = validated_data.pop('address', None)
        validated_data.update(
            {
                "user": self.context['request'].user
            }
        )
        instance = super(ProductSerializer, self).update(instance, validated_data)
        if category:
            category_obj = Category.objects.filter(pk=category['id']).first()
            if not category_obj:
                raise ValidationError(handle_404('invalid input', 'Category'))
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
        obj = instance.address
        if address:
            obj = Address.objects.filter(**address).first()
            if not obj:
                obj = Address.objects.create(**address)
                instance.address = obj
                instance.save()
        instance.address = obj
        instance.save()
        return instance

    class Meta:
        model = Product
        fields = (
            'id', 'user', 'category', 'title_current', 'description', 'image', 'price', 'min_price',
            'current_price',
            'increase_amount',
            'attrs',
            'description_ar',
            'description_en',
            'type',
            'reviews',
            'title',
            'start_time',
            'end_time',
            'title_ar',
            'new',
            'tags',
            'used',
            'sale',
            'stock',
            'title_en',
            'description_current',
            'product_orders',
            'discount',
            'media',
            'active',
            'amount',
            'address',
        )


class AttributSerializer(serializers.ModelSerializer):
    values = AttributDetailsSerializer(many=True)
    title_current = serializers.CharField(read_only=True, source='title')
    title = serializers.SerializerMethodField()
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)

    def get_title(self, instance):
        return {
            "en": instance.title_en,
            "ar": instance.title_ar
        }

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
        fields = ('id', 'title', 'title_current', 'values', 'title_ar', 'title_en')


class AuctionOrderSerializer(serializers.ModelSerializer):
    current_payment = serializers.DecimalField(read_only=True, decimal_places=3, max_digits=10)
    directed = serializers.BooleanField(required=False)
    auction_order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        required=False
    )
    status = serializers.CharField(read_only=True)
    increase_user = serializers.DecimalField(max_digits=10, decimal_places=3, write_only=True, required=False)

    def create(self, validated_data):
        request = self.context['request']
        validated_data.update({"user": request.user})
        address = request.data.get('address', None)
        direct = validated_data.get('directed', False)
        address = get_object_or_404(Address, pk=address)
        auction_product = validated_data.get('auction_product')
        max_payment = auction_product.current_price
        new_order = Order.objects.create(
            user=request.user,
            address=address,
            status=Order.PENDING)
        instance = AuctionOrder.objects.create(
            order_product=new_order,
            auction_product=auction_product,
            direct=direct,
            current_payment=max_payment
        )

        # new_order.auction_orders.add(instance)
        increase_amount = request.data.get('increase_amount', None)
        increase_user = validated_data.get('increase_user', None)
        if increase_amount:
            new_value = max_payment + auction_product.increase_amount
            if request.user.wallet.amount >= new_value:
                instance.current_payment = new_value
                auction_product.current_price += auction_product.increase_amount
        elif increase_user:
            new_value = max_payment + increase_user
            if request.user.wallet.amount >= new_value:
                instance.current_payment = new_value
                auction_product.current_price += increase_user
        elif direct and request.user.wallet.amount >= instance.auction_product.price:
            send_mail('New Direct payemnt request', 'A stunning message', settings.EMAIL_HOST_USER,
                      ['ahmadc@gmail.com'])

        instance.save()
        new_order.auction_orders.add(instance)
        auction_product.auction_orders.add(instance)
        new_order.save()
        auction_product.save()
        OrderLog.objects.create(order=instance, auctions=True)
        return instance

    def update(self, instance, validated_data):
        request = self.context['request']
        direct = validated_data.get('directed', False)
        increase_amount = request.data.get('increase_amount', None)
        increase_user = validated_data.get('increase_user', None)
        max_payment = instance.current_price
        if increase_amount:
            new_value = max_payment + instance.increase_amount
            if request.user.wallet.amount >= new_value:
                instance.current_payment = new_value
                instance.current_price += instance.increase_amount
        elif increase_user:
            new_value = max_payment + increase_user
            if request.user.wallet.amount >= new_value:
                instance.current_payment = new_value
                instance.current_price += increase_user
        elif direct and request.user.wallet.amount >= instance.auction_product.price:
            send_mail('New Direct payemnt request', 'A stunning message', settings.EMAIL_HOST_USER,
                      ['ahmadc@gmail.com'])
        instance.save()
        return instance

    class Meta:
        model = AuctionOrder
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField(read_only=True)
    product_orders = ProductOrderSerializer(many=True)
    username = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    shipping_company = serializers.PrimaryKeyRelatedField(queryset=ShippingCompany.objects.all(), write_only=True)
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), write_only=True)

    def get_username(self, instance):
        return instance.user.email

    def get_company(self, instance):
        return instance.shipping_company.name

    def get_location(self, instance):
        return instance.address.address

    def get_total_cost(self, instance):
        raw_cost = sum([elment.price for elment in instance.product_orders.all()])
        company_tax = (instance.shipping_company.tax * raw_cost) / 100
        cost_with_tax = raw_cost + company_tax
        final_cost = cost_with_tax + instance.shipping_company.cost
        return final_cost

    def create(self, validated_data):
        product_orders = validated_data.pop('product_orders')
        validated_data.update({"user": self.context['request'].user})
        instance = super(OrderSerializer, self).create(validated_data)
        for product_order in product_orders:
            quantity = product_order.get('quantity')
            validate_product_order(product_order)
            new_pd = ProductOrder.objects.create(**product_order)
            new_pd.order = instance
            if new_pd.product.product_type in ['bazaar', 'shops']:
                new_pd.product.amount = new_pd.product.amount - quantity
                new_pd.product.save()
                instance.save()
            instance.product_orders.add(new_pd)
            instance.save()

        OrderLog.objects.create(order=instance, auctions=False)
        return instance

    def update(self, instance, validated_data):
        product_orders = validated_data.pop('product_orders')
        instance = super(OrderSerializer, self).update(instance, validated_data)
        for product_order in product_orders:
            item = get_object_or_404(ProductOrder, pk=product_order.pop('id'))
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
    name_current = serializers.CharField(read_only=True, source='title')
    address = AddressCompanySerializer()
    name = serializers.SerializerMethodField(required=False)

    def get_name(self, instance):
        return {
            "en": instance.name_en,
            "ar": instance.name_ar
        }

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


class PageSerializer(serializers.ModelSerializer):
    slider_content = SliderSerializer(read_only=True, many=True, source='sliders')
    about = serializers.SerializerMethodField()
    about_current = serializers.CharField(read_only=True, source='about')
    about_en = serializers.CharField(write_only=True)
    about_ar = serializers.CharField(write_only=True)
    image = Base64ImageField(required=False)

    def get_about(self, instance):
        return {
            'en': instance.about_en,
            'ar': instance.about_ar,
        }

    class Meta:
        model = Page
        fields = ('id',
                  'slider_content',
                  'about_current',
                  'about_en',
                  'page_type',
                  'image',
                  'about',
                  'about_ar')


class OrderLogSerializer(serializers.ModelSerializer):
    by = serializers.StringRelatedField()

    class Meta:
        model = OrderLog
        fields = '__all__'
