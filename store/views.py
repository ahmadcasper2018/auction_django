from django.core.files import File
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .permessions import ProductPermession
from .models import *
from .serializers import *


# Create your views here.


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (ProductPermession,)

    def get_queryset(self):
        queryset = super(ProductViewSet, self).get_queryset()
        cat_id = self.request.query_params.get('cat_id', None)
        category = self.request.query_params.get('category', None)
        my_products = self.request.query_params.get('my_products', None)
        if category:
            queryset = queryset.filter(category__title=category)
        if cat_id:
            queryset = queryset.filter(category__pk=int(cat_id))
        if (not my_products) and (not (self.request.user.is_staff or self.request.user.is_superuser)):
            queryset = queryset.filter(status='a')
        if my_products:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        for file in self.request.FILES.getlist('file'):
            media_obj = Media.objects.create(file=File(file))
            response.append(media_obj.pk)
        return Response(data={"ids": response}, status=200)


class AttributDetailsViewSet(viewsets.ModelViewSet):
    queryset = AttributDetails.objects.all()
    serializer_class = AttributDetailsSerializer


class ProductAttributViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribut.objects.all()
    serializer_class = ProductAttribut


class CategoryAttributeViewSet(viewsets.ModelViewSet):
    queryset = CategoryAttribute.objects.all()
    serializer_class = CategoryAttributSerializer
