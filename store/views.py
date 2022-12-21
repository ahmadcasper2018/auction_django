import random

from django.core.files import File
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


class AboutUs(TemplateView):
    template_name = 'direct_request.html'


def measure_similarity(list1, list2):
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

    def get_queryset(self):
        queryset = super(ProductViewSet, self).get_queryset()
        cat_id = self.request.query_params.get('cat_id', None)
        brands = self.request.query_params.get('brands', None)
        my_products = self.request.query_params.get('my_products', None)

        if brands:
            brands = brands.split(',')
            queryset = queryset.filter(category__brands__in=brands)
        if cat_id:
            queryset = queryset.filter(category__pk=int(cat_id))
        # if (not my_products) and (not (self.request.user.is_staff or self.request.user.is_superuser)):
        #     queryset = queryset.filter(status='a')
        if my_products:
            queryset = queryset.filter(user=self.request.user)

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
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
        serializer = self.serializer_class(data=request.data, many=True, context={'request': request})
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

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

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

    # def get_queryset(self):
    #     return super(MediaViewSet, self).get_queryset().filter(product__user=self.request.user)

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
        data = {}
        page_type = self.request.query_params.get('page_type', None)
        if page_type:
            queryset = queryset.filter(page_type=page_type).first()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        if not page_type:
            serializer = self.get_serializer(queryset, many=True)
            data = {'pages': serializer.data}
        else:
            serializer = self.get_serializer(queryset)
            data = {'page_type': serializer.data['page_type'], 'id': serializer.data['id'], 'page': serializer.data}
        conatct = ContactSettings.objects.first()
        contact_serializer = ContactSettingsSerializer(conatct)

        data.update({
            'contact_settings': contact_serializer.data
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
