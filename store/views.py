import random

from django.core.files import File
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from general.models import ContactSettings
from general.permessions import SettingsAccress
from general.serializers import ContactSettingsSerializer
from .filters import ProductFilter
from .pagination import ProductsPagination
from .permessions import ProductPermession, BrandPermession
from .models import *
from .serializers import *
from django_filters import rest_framework as filters

# Create your views here.

# def approve_request(request, pk):
#     auction = get_object_or_404(AuctionOrder, pk=pk)
#     product = auction.auction_product
#     client = auction.order_product.user
#     return render_to_string('direct_request.html', {'context': {}})


from django.views.generic.base import TemplateView


def flat_2D(l):
    return list(set([j for sub in l for j in sub]))


class AboutUs(TemplateView):
    template_name = 'direct_request.html'


def measure_similarity(list1, list2):
    if not (list1 or list2):
        return float(0)
    return len(set(list1) & set(list2)) / float(len(set(list1) | set(list2))) * 100


def flatten_values(product: Product):
    last_values = [j for sub in product.tags for j in sub]
    return last_values


def find_similar_products(product: Product):
    response = []
    count_added = 0
    percent = (product.price * 2) / 100
    min_price = product.price - percent
    max_price = product.price + percent
    current_values = flatten_values(product)
    similar_cat = Product.objects.filter(category=product.category)
    excluded = similar_cat.exclude(pk=product.pk)
    for prod in excluded.filter(category=product.category):
        product_values = flatten_values(prod)
        similarity = measure_similarity(current_values, product_values)
        if similarity > 80.0 and count_added < 10:
            count_added += 1
            response.append(prod)
    products = Product.objects.all().filter(price__lt=max_price, price__gt=min_price).exclude(pk=product.pk)
    response.extend(products)
    if len(response) > 10:
        response = response[:10]
    random.shuffle(response)
    return response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (ProductPermession,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = ProductsPagination

    # @method_decorator(cache_page(60 * 60))
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        cat_id = self.request.query_params.get('category', None)
        categories = Category.objects.all()
        colors_flatten = []
        response = {}
        bounds = {}
        sizes_flatten = []
        brands_flatten = []
        if cat_id:
            categories = categories.filter(pk=cat_id).first()
            orderd_products = categories.products.all().order_by('price')
            minimum = orderd_products.first().price
            maximum = orderd_products.last().price
            bounds.update({
                'min': minimum,
                'max': maximum
            })
            colors = [i.attribute_values('color') for i in orderd_products]
            sizes = [i.attribute_values('size') for i in orderd_products]
            brands_flatten = list(set(categories.brands_list))
            colors_flatten = flat_2D(colors)
            sizes_flatten = flat_2D(sizes)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
            if bounds:
                data.update(bounds)
            if brands_flatten:
                data.update({'brands': brands_flatten})
            if colors_flatten:
                data.update({'colors': colors_flatten})
            if sizes_flatten:
                data.update({'sizes': sizes_flatten})
            return Response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        response.update({"result": data})
        if brands_flatten:
            response.update({'brands': brands_flatten})

        return Response(response)

    def get_queryset(self):
        queryset = super(ProductViewSet, self).get_queryset()
        cat_id = self.request.query_params.get('cat_id', None)
        brands = self.request.query_params.get('brands', None)
        my_products = self.request.query_params.get('my_products', None)
        tags_search = self.request.query_params.get('tags_search', None)

        if brands:
            brands = brands.split(',')
            queryset = queryset.filter(brand__title__in=brands)
        if cat_id:
            queryset = queryset.filter(category__pk=int(cat_id))
        # if (not my_products) and (not (self.request.user.is_staff or self.request.user.is_superuser)):
        #     queryset = queryset.filter(status='a')
        if my_products:
            queryset = queryset.filter(user=self.request.user)

        if tags_search:
            products = super(ProductViewSet, self).get_queryset()
            similar_pks = []
            tags_search = tags_search.split(',')
            for product in products:
                if tags_search in product.tags_show:
                    similar_pks.append(product.pk)

            queryset = queryset.filter(pk__in=similar_pks)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views.viewers += 1
        instance.views.save()
        similar_products = find_similar_products(instance)
        serializer = self.get_serializer(instance)

        similar = self.get_serializer(similar_products, many=True)

        data = serializer.data
        data.update(
            {"similar_products": similar.data}
        )
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            products = serializer.save()
            instance = products
            old_price = instance.price
            sale = request.data.get('sale', False)
            if sale:
                discount = instance.discount
                discounted_value = (instance.price * discount) / 100
                instance.price = instance.price - discounted_value
                instance.save()
            if old_price == instance.price:
                old_price = None
            response = serializer.data
            response.update(
                {'old_price': old_price}
            )
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            errors = {'message': 'You have entered invalid data for this product'}
            errors.update({'errors': serializer.errors})
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # @method_decorator(cache_page(60 * 60))
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(CategoryViewSet, self).get_queryset()
        code = self.request.query_params.get('code', None)
        if code:
            qs = qs.filter(code=code)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (instance.code is None):
            raise ValidationError("You can't delete this type of categories")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShippingCompanyViewSet(viewsets.ModelViewSet):
    queryset = ShippingCompany.objects.all()
    serializer_class = ShippingCompanySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        return super(OrderViewSet, self).get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class ProductOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductOrder.objects.all()
    serializer_class = ProductOrderSerializer

    def get_queryset(self):
        return super(ProductOrderViewSet, self).get_queryset().filter(order__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class AuctionOrderRequestViewSet(viewsets.ModelViewSet):
    queryset = AuctionOrder.objects.all()
    serializer_class = AuctionOrderSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['post', 'get', 'delete'])
    def handle_request(self, request):
        if request.method == 'POST':
            validated_data = self.request.data
            user = self.request.user
            increase_amount = validated_data.get('increase_amount', None)
            increase_user = validated_data.get('increase_user', None)
            directed = validated_data.get('directed', False)
            auction_product = Product.objects.get(pk=validated_data.get('auction_product'))

            errors = {}

            if auction_product.auction_success:
                errors[
                    "auction_product"] = "these product was bought successfully"

            if not (increase_amount or increase_user or directed):
                errors[
                    "auction_product"] = "You have to enter amount to increas or press the adding button"

            if directed:
                if not (user.wallet.amount >= auction_product.price):
                    errors["direct payment"] = "You don't have enough funds in your wallet"

            if errors:
                raise serializers.ValidationError(errors)
            else:
                current_product = Product.objects.get(pk=validated_data.get('auction_product'))
                max_payment = current_product.current_price
                if not user.auction_requests.filter(auction_product=validated_data.get('auction_product')):
                    instance = AuctionOrder.objects.create(
                        auction_product=current_product,
                        direct=validated_data.get('directed', False),
                        current_payment=max_payment,
                        user=user
                    )
                else:
                    instance = user.auction_requests.get(auction_product=validated_data.get('auction_product'))
                increase_amount = validated_data.get('increase_amount', None)
                increase_user = validated_data.get('increase_user', None)
                if increase_amount:
                    instance.current_payment += increase_amount
                    current_product.current_price += increase_amount
                elif increase_user:
                    instance.current_payment += increase_user
                    current_product.current_price += increase_user
                elif directed:
                    if not (user.wallet.amount >= current_product.price):
                        raise ValidationError('you dont have enough money to buy this product')
                    else:
                        user.wallet.amount -= current_product.price
                        user.wallet.save()
                        current_product.auction_success = True
                        instance.status = AuctionOrder.APPROVED
                        current_product.save()
                instance.status = AuctionOrder.PENDING
                if current_product.current_price >= current_product.price:
                    if not (user.wallet.amount >= current_product.price):
                        raise ValidationError('you dont have enough money to buy this product')
                    else:
                        user.wallet.amount -= current_product.price
                        user.wallet.save()
                        user.save()
                        current_product.auction_success = True
                        instance.status = AuctionOrder.APPROVED
                        instance.save()
                        current_product.save()

                current_product.save()
                instance.save()
                return Response(data=self.serializer_class(instance).data, status=200)

    def get_queryset(self):
        qs = super(AuctionOrderRequestViewSet, self).get_queryset()
        product = self.request.query_params.get('product', None)
        if product:
            qs = qs.filter(auction_product__pk=product)
        return qs

        # .filter(auction_product__user=self.request.user)


class AttributViewSet(viewsets.ModelViewSet):
    queryset = Attribut.objects.all()
    serializer_class = AttributSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def get_queryset(self):
        qs = super(MediaViewSet, self).get_queryset()
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            qs = qs.filter(product__pk=product_id)

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        response = []
        file = self.request.FILES.getlist('file')[0]
        media_obj = Media.objects.create(file=File(file))
        response.append(media_obj.pk)
        data = dict(request.data)
        data.pop('file')
        cleaned_data = {key: value[0] for key, value in data.items()}
        for key, value in cleaned_data.items():
            setattr(media_obj, key, value)
        media_obj.save()
        return Response(data={"ids": response}, status=200)

    @action(detail=False, methods=['post'])
    def upload_product_media(self, request):
        alt = request.data.get('alt')
        value = request.data.get('value')
        attribute = request.data.get('attribute')
        if not alt:
            raise ValidationError(create_error('Alt', "enter a valid Alt"))
        if not value:
            raise ValidationError(create_error('value', "enter a value"))
        else:
            if not AttributDetails.objects.filter(pk=value).exists():
                raise ValidationError(create_error('value', "enter a value"))
        if not attribute:
            raise ValidationError(create_error('value', "enter a value"))
        else:
            if not Attribut.objects.filter(pk=value).exists():
                raise ValidationError(create_error('value', "enter a value"))
        product_id = self.request.query_params.get('product_id', None)
        if not product_id:
            raise ValidationError(create_error('Product', "enter a valid product"))
        file = dict(request.FILES).get('file', None)
        if not file:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'Error': 'you have to enter a valid media'})
        file = file[0]
        product = Product.objects.get(pk=product_id)
        attribute = Attribut.objects.get(pk=attribute)
        value =  AttributDetails.objects.get(pk=value)
        new_medias = []
        new_media = Media.objects.create(file=file, alt=alt, value=value)
        new_media.attributes.add(attribute)
        product.media.add(new_media)
        new_medias.append(new_media)

        return Response(status=status.HTTP_201_CREATED, data=MediaSerializer(new_medias, many=True).data)


class SliderMediaViewSet(viewsets.ModelViewSet):
    queryset = SliderMedia.objects.all()
    serializer_class = SliderMediaSerializer

    # def get_queryset(self):
    #     return super(MediaViewSet, self).get_queryset().filter(product__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        response = []
        file = self.request.FILES.getlist('file')[0]
        media_obj = SliderMedia.objects.create(file=File(file))
        response.append(media_obj.pk)
        data = dict(request.data)
        data.pop('file')
        cleaned_data = {key: value[0] for key, value in data.items()}
        for key, value in cleaned_data.items():
            setattr(media_obj, key, value)
        media_obj.save()

        return Response(data={"ids": response}, status=200)


class AttributDetailsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttributDetails.objects.all()
    serializer_class = AbstractAttributDetailsSerializer

    @action(detail=False, methods=['get'])
    def get_list(self, request):
        objs = request.data['objects']
        queryset = self.queryset.filter(pk__in=objs)
        serializer = self.serializer_class(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductAttributViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribut.objects.all()
    serializer_class = ProductAttribut


class CategoryAttributeViewSet(viewsets.ModelViewSet):
    queryset = CategoryAttribute.objects.all()
    serializer_class = CategoryAttributSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = (BrandPermession,)

    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        qs = super(BrandViewSet, self).get_queryset()
        if category:
            category = get_object_or_404(Category, pk=category)
            qs = qs.filter(Q(category=category) | Q(products__category=category))
        return qs


class SliderViewSet(viewsets.ModelViewSet):
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class ProductValuesViewset(viewsets.ModelViewSet):
    queryset = AttributValue.objects.all()
    serializer_class = AttributeValueSerializer
    permission_classes = (IsAuthenticated,)


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (SettingsAccress,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        products = Product.objects.none()
        news = Product.objects.none()
        popular = Product.objects.none()
        sales = Product.objects.none()
        try:
            logo = Media.objects.filter(is_logo=True).last()
        except Logo.DoesNotExist:
            raise ValidationError('please enter a valid logo first')
        page_type = self.request.query_params.get('page_type', None)
        if page_type:
            queryset = queryset.filter(page_type=page_type).first()
            if page_type != 'home':
                products = Product.objects.filter(category__code=page_type).order_by('-views__viewers')

            else:
                products = Product.objects.all().order_by('-views__viewers')
            sales = products.filter(sale=True)
            news = products.filter(new=True)
        if sales and len(sales) > 10:
            sales = sales[:10]
        if news and len(news) > 10:
            news = news[:10]
        if products and len(products) > 10:
            popular = products[:10]
        else:
            popular = products

        if not page_type:
            serializer = self.get_serializer(queryset, many=True)
            data = {'pages': serializer.data}
        else:
            serializer = self.get_serializer(queryset)
            data = {'page_type': serializer.data['page_type'],
                    'id': serializer.data['id'],
                    'page': serializer.data,
                    'new': ProductSerializer(news, many=True).data,
                    'popular': ProductSerializer(popular, many=True).data,
                    'sale': ProductSerializer(sales, many=True).data,
                    }
        conatct = ContactSettings.objects.first()
        contact_serializer = ContactSettingsSerializer(conatct)
        contacts = contact_serializer.data
        file_path = ''
        prefix = "https://wabel.incareg.com"
        logo_data = MediaSerializer(logo).data
        if logo:
            file_path = prefix + logo_data['file']
        logo_data['file'] = file_path
        contacts.update(
            {'logo': logo_data}
        )

        data.update({
            'contact_settings': contacts
        })
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        page_type = instance.page_type
        products = Product.objects.all().order_by('-views__viewers')
        popular = products
        if len(popular) > 20:
            popular = popular[:20]
        if page_type != Page.HOME:
            products = products.filter(category__title=page_type)
        new_products = products.filter(new=True)
        used_products = products.filter(user=True)
        if len(new_products) > 12:
            new_products = new_products[:12]
        if len(used_products) > 12:
            used_products = used_products[:12]
        new_serializer = ProductSerializer(new_products, many=True)
        used_serializer = ProductSerializer(used_products, many=True)
        popular_serializer = ProductSerializer(popular, many=True)
        logo = Logo.objects.last()
        conatct = ContactSettings.objects.first()
        contact_serializer = ContactSettingsSerializer(conatct)
        data = {'page': serializer.data}
        if logo:
            serializer = LogoSerializer(logo)
            data.update(
                {
                    'logo': serializer.data
                }
            )
        data.update({
            'contact_settings': contact_serializer.data,
            "new_products": new_serializer.data,
            "used_products": used_serializer.data,
            "popular_products": popular_serializer.data,

        })
        return Response(data)


class LogoViewSet(viewsets.ModelViewSet):
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer


class OrderLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderLog.objects.all()
    serializer_class = OrderLogSerializer

    def get_queryset(self):
        auctions = self.request.query_params.get('auctions', None)
        qs = super(OrderLogViewSet, self).get_queryset()
        if auctions:
            qs = qs.filter(auctions=True)
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(by=self.request.user)
        return qs
