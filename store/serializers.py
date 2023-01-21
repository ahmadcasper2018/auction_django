from django.db.models import Max
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from authentication.models import User
from authentication.serializers import SubUserSerializer
from location.models import Address, City
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


def create_error(field, error):
    response = {'message': f"Invalid {field}"}
    response.update(
        {
            'errors': {
                field: error
            }
        }
    )
    return response


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
    address = serializers.SerializerMethodField()
    city_current = serializers.SerializerMethodField()

    def get_city_current(self, instance):
        return instance.city.title

    def get_address(self, instance):
        return instance.address

    class Meta:
        model = Address
        fields = ('city', 'address', 'city_current')


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
        fields = ('id', 'file', 'type', 'attributes', 'alt', 'value', 'product')


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


class CategoryAttributSerializer(serializers.ModelSerializer):
    title_current = serializers.SerializerMethodField(read_only=True)
    values = serializers.SerializerMethodField(read_only=True)

    def get_title_current(self, instance):
        if instance.attribut:
            return instance.attribut.title
        else:
            return ''

    def get_values(self, instance):
        objs = instance.attribut.values.all()
        if not objs:
            return []
        else:
            return AttributDetailsSerializer(objs, many=True).data

    class Meta:
        model = CategoryAttribute
        fields = ('id', 'attribut', 'title_current', 'values')


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
    title_current = serializers.SerializerMethodField(read_only=True)
    code = serializers.SerializerMethodField()

    def get_code(self, instance):
        return instance.attribut.code

    def get_title(self, instance):
        return {
            "en": instance.attribut.title_en,
            "ar": instance.attribut.title_ar
        }

    def get_title_current(self, instance):
        return instance.attribut.title

    class Meta:
        model = ProductAttribut
        fields = ('id', 'attribut',
                  'title',
                  'values',
                  'code',
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
    brands = BrandSerializer(read_only=True, many=True)
    category_attrs = CategoryAttributSerializer(many=True, read_only=True)
    products = CategoryProductSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)
    banner = Base64ImageField(required=False)
    title_current = serializers.CharField(read_only=True, source='title')
    title = serializers.SerializerMethodField(required=False)
    title_ar = serializers.CharField(write_only=True)
    title_en = serializers.CharField(write_only=True)
    parent_current = serializers.SerializerMethodField()

    def get_parent_current(self, instance):
        return instance.parent_title

    def validate(self, attrs):
        code = attrs.get('code', None)
        atttrs = self.context['request'].data.get('category_attrs', None)

        if atttrs:
            for attr in atttrs:
                get_object_or_404(Attribut, pk=attr['attribut'])

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
        attrs = self.context['request'].data.get('category_attrs')
        instance = super(CategorySerializer, self).create(validated_data)
        if attrs:
            for attr in attrs:
                attr = get_object_or_404(Attribut, pk=attr['attribut'])
                obj, created = CategoryAttribute.objects.get_or_create(attribut=attr)
                obj.category = instance
                obj.save()
                instance.category_attrs.add(obj)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        attrs = self.context['request'].data.get('category_attrs')

        instance = super(CategorySerializer, self).update(instance, validated_data)
        if attrs:
            instance.category_attrs.clear()
            for attr in attrs:
                attr = get_object_or_404(Attribut, pk=attr['attribut'])
                obj, created = CategoryAttribute.objects.get_or_create(attribut=attr)
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
    attrs = AttributDetailsSerializer(read_only=True, many=True)

    # product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    # directed_bazar = serializers.BooleanField()

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    class Meta:
        model = ProductOrder
        fields = '__all__'


class ProductBrandSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title_current = serializers.CharField(read_only=True, source='title')


class ProductSerializer(serializers.ModelSerializer):
    # user = UserProductSerializer()
    category = ProductCategorySerializer(read_only=True)
    attrs = ProductAttributSubSerializer(many=True, required=False, read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    product_orders = ProductOrderSerializer(many=True, read_only=True)

    media = MediaSerializer(many=True, read_only=True)
    image = Base64ImageField(required=False)
    address = AddressCompanySerializer(read_only=True)
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
    current_price = serializers.DecimalField(max_digits=10, decimal_places=3, read_only=True)
    tags = serializers.SerializerMethodField()

    def get_tags(self, instance):
        return instance.tags_show

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, instance):
        return instance.product_type

    def validate(self, attrs):
        data = self.context['request'].data
        title_en = data.get('title_en')
        if self.context['request'].method == 'POST':
            if len(Product.objects.filter(title=title_en)) > 1:
                raise ValidationError(create_error('already exists', 'product'))
        category = data.get('category', None)

        if not category:
            raise ValidationError(create_error('Category', 'you have to enter a valid category'))
        else:
            if not Category.objects.filter(pk=category).exists():
                raise ValidationError(create_error('Not found', 'Category'))

        return attrs

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

    def get_avg_reviews(self, instance):
        return instance.avg_reviews

    def create(self, validated_data):
        data = self.context['request'].data
        category = data.get('category')
        brand = data.pop('brand', None)
        attrs = self.context['request'].data.get('attrs', None)
        address = validated_data.pop('address', None)
        validated_data.update({"user": self.context['request'].user})
        instance = super(ProductSerializer, self).create(validated_data)
        instance.current_price = validated_data.get('min_price')
        category = Category.objects.get(pk=category)
        if brand:
            if not Brand.objects.filter(pk=brand).exists():
                raise ValidationError(create_error('Brand', 'you have to enter a valid brand'))
            else:
                instance.brand = Brand.objects.get(pk=brand)

        instance.category = category
        if attrs:
            for atr in attrs:
                values_new = atr['values']
                attribute_id = atr['attribute']
                attribute = get_object_or_404(Attribut, pk=attribute_id)
                values_obs = AttributDetails.objects.filter(pk__in=values_new)
                new_pd = ProductAttribut.objects.create(
                    product=instance,
                    attribut=attribute,
                )
                for value in values_obs:
                    new_pd.values.add(value)
                new_pd.save()

        if address:
            obj = Address.objects.filter(**address).first()
            if not obj:
                obj = Address.objects.create(**address)
                instance.address = obj
                instance.save()
            instance.address = obj
        ProductViewers.objects.create(product=instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        data = self.context['request'].data
        category = data.get('category')
        brand = data.pop('brand', None)
        attrs = self.context['request'].data.get('attrs', None)
        address = validated_data.pop('address', None)
        validated_data.update({"user": self.context['request'].user})
        category = Category.objects.get(pk=category)
        if brand:
            if not Brand.objects.filter(pk=brand).exists():
                raise ValidationError(create_error('Brand', 'you have to enter a valid brand'))
            else:
                instance.brand = Brand.objects.get(pk=brand)
        instance.current_price = validated_data.get('min_price')
        instance.category = category
        if attrs:
            for atr in attrs:
                values_new = atr['values']
                attribute_id = atr['attribute']
                attribute = get_object_or_404(Attribut, pk=attribute_id)
                values_obs = AttributDetails.objects.filter(pk__in=values_new)
                new_pd, created = ProductAttribut.objects.get_or_create(
                    product=instance,
                    attribut=attribute,
                )

                new_pd.values.set(list(values_obs))
                new_pd.save()

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
            'brand',
            'reviews',
            'title',
            'start_time',
            'end_time',
            'auction_success',
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
        values = validated_data.pop('values', None)
        instance = super(AttributSerializer, self).update(instance, validated_data)
        if values:
            for value in values:
                obj = get_object_or_404(AttributDetails, pk=int(value['id']))
                obj.value = value.get('value', obj.value)
                obj.value_en = value.get('value', obj.value_en)
                obj.value_ar = value.get('value', obj.value_ar)
                obj.save()
        return instance

    class Meta:
        model = Attribut
        fields = ('id', 'title', 'title_current', 'values', 'title_ar', 'title_en', 'code')


class AuctionOrderSerializer(serializers.ModelSerializer):
    current_payment = serializers.IntegerField(read_only=True)
    directed = serializers.BooleanField(required=False)
    status = serializers.CharField(read_only=True)
    increase_amount = serializers.BooleanField(write_only=True)
    increase_user = serializers.DecimalField(max_digits=10, decimal_places=3, write_only=True, required=False)

    def validate(self, data):
        request = self.context['request']
        user = request.user
        increase_amount = data.get('increase_amount', None)
        increase_user = data.get('increase_user', None)
        directed = data.get('directed', False)
        auction_product = data.get('auction_product')
        address = data.get('address')
        errors = {}
        if not address:
            errors['address'] = "you must enter a valid address"
        if not directed and not increase_amount and not increase_user:
            errors[
                "auction_product"] = "You must either place a bid, increase the bid by a certain amount, or buy it directly"
        if increase_amount:
            new_value = auction_product.current_price + increase_amount
            if user.wallet.amount < new_value:
                errors["increase_amount"] = "You don't have enough funds in your wallet"
        elif increase_user:
            new_value = auction_product.current_price + increase_user
            if user.wallet.amount < new_value:
                errors["increase_user"] = "You don't have enough funds in your wallet"
        if errors:
            raise serializers.ValidationError(errors)
        return data

    class Meta:
        model = AuctionOrder
        fields = '__all__'


class SubOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    price = serializers.SerializerMethodField(read_only=True)
    attrs = AttributDetailsSerializer(read_only=True, many=True)
    product = ProductSerializer(read_only=True)

    # product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    # directed_bazar = serializers.BooleanField()

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    class Meta:
        model = ProductOrder
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField(read_only=True)
    product_orders = SubOrderSerializer(read_only=True, many=True)
    status = serializers.CharField(read_only=True)
    username = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    shipping_company = serializers.PrimaryKeyRelatedField(queryset=ShippingCompany.objects.all(), write_only=True)
    lang = serializers.CharField(required=True)
    lat = serializers.CharField(required=True)
    address = serializers.CharField(required=True)

    def validate(self, attrs):

        product_orders = self.context['request'].data.get('product_orders', None)
        end_price = 0
        user = self.context['request'].user
        if not product_orders:
            raise ValidationError(create_error('Invalid Input', 'product_orders'))
        else:
            for data in product_orders:
                product_id = data.get("product", None)
                if not Product.objects.filter(pk=product_id).exists():
                    raise ValidationError(create_error('Not found', 'product'))
                else:
                    product = Product.objects.get(pk=product_id)
                    end_price += (product.price - (product.price * product.discount / 100))
                quantity = data.get("quantity", 1)
                values = data.get('values', None)
                if quantity > product.amount:
                    raise ValidationError(create_error('amount', 'you exceded the avaliable amount'))
            if end_price > user.wallet.amount:
                raise ValidationError(create_error('Wallet', 'You dont have enought funds'))

        return attrs

    def get_username(self, instance):
        return instance.user.email

    def get_company(self, instance):
        return instance.shipping_company.name

    def get_total_cost(self, instance):
        raw_cost = sum([elment.price for elment in instance.product_orders.all()])
        company_tax = (instance.shipping_company.tax * raw_cost) / 100
        cost_with_tax = raw_cost + company_tax
        final_cost = cost_with_tax + instance.shipping_company.cost
        return final_cost

    def create(self, validated_data):
        product_orders = self.context['request'].data.pop('product_orders')
        user = self.context['request'].user
        validated_data.update({"user": user})
        instance = super(OrderSerializer, self).create(validated_data)
        for product_order in product_orders:
            product_id = product_order.pop('product', None)
            values = product_order.pop('values', None)
            product = Product.objects.get(pk=product_id)
            quantity = product_order.get('quantity', 1)
            new_pd = ProductOrder.objects.create(product=product, **product_order)
            new_pd.order = instance
            if values:
                value_objs = AttributDetails.objects.filter(pk__in=values)
                for value in value_objs:
                    new_pd.attrs.add(value)
            new_pd.product.amount = new_pd.product.amount - quantity
            new_pd.product.save()
            new_pd.sub_price = (product.price - (product.price * product.discount / 100)) * quantity
            new_pd.save()
            instance.product_orders.add(new_pd)
            user.wallet.amount -= (product.price - (product.price * product.discount / 100))
            user.wallet.save()
            user.save()
        OrderLog.objects.create(order=instance)
        instance.status = Order.PENDING
        instance.save()
        return instance

    def update(self, instance, validated_data):
        product_orders = validated_data.pop('product_orders', None)
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
    address = AddressCompanySerializer(read_only=True)
    name_current = serializers.CharField(read_only=True, source='name')
    name = serializers.SerializerMethodField(required=False)
    name_en = serializers.CharField(write_only=True)
    name_ar = serializers.CharField(write_only=True)

    def get_name(self, instance):
        return {
            "en": instance.name_en,
            "ar": instance.name_ar
        }

    def create(self, validated_data):
        address = self.context['request'].data.pop('address')
        if not City.objects.filter(pk=address['city']).exists():
            raise ValidationError(create_error('city', 'please enter a valid city'))
        city = City.objects.get(pk=address['city'])
        address = address['address']
        location, created = Address.objects.get_or_create(city=city, address=address)
        validated_data.update({"address": location})
        instance = super(ShippingCompanySerializer, self).create(validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        address_data = self.context['request'].data.pop('address', {})
        name_en = validated_data.pop('name_en', None)
        name_ar = validated_data.pop('name_ar', None)
        cost = validated_data.pop('cost', None)
        phone = validated_data.pop('phone', None)

        # Update fields with new data
        instance.name_en = name_en or instance.name_en
        instance.name_ar = name_ar or instance.name_ar
        instance.cost = cost or instance.cost
        instance.phone = phone or instance.phone
        if not City.objects.filter(pk=address_data['city']).exists():
            raise ValidationError(create_error('city', 'please enter a valid city'))
        city = City.objects.get(pk=address_data['city'])
        addres = address_data['address']
        address = Address.objects.filter(city=city, address=addres).first()
        if not address:
            address = Address.objects.create(city=city, address=addres)
        instance.address = address
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


class SubOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    price = serializers.SerializerMethodField(read_only=True)
    attrs = AttributDetailsSerializer(read_only=True, many=True)
    product = ProductSerializer(read_only=True)

    # product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    # directed_bazar = serializers.BooleanField()

    def get_price(self, instance):
        return instance.product.price * instance.quantity

    class Meta:
        model = ProductOrder
        fields = '__all__'
