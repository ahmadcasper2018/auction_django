import random

from django.core.files import File
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .permessions import ProductPermession, BrandPermession
from .models import *
from .serializers import *
from django_filters import rest_framework as filters


# Create your views here.


def measure_similarity(list1, list2):
    return len(set(list1) & set(list2)) / float(len(set(list1) | set(list2))) * 100


def flatten_values(product: Product):
    raw_values = [list(i.values()) for i in product.tags]
    last_values = [j for sub in raw_values for j in sub]
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
        # if self.request.user.is_anonymous:
        #     return AuctionOrder.objects.none()
        return super(AuctionOrderRequestViewSet, self).get_queryset()
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
