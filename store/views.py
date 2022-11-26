from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import *
from .serializers import *


# Create your views here.


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return super(ProductViewSet, self).get_queryset().filter(user=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShippingCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShippingCompany.objects.all()
    serializer_class = ShippingCompanySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return super(OrderViewSet, self).get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


class ProductOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ProductOrderSerializer

    def get_queryset(self):
        return super(ProductOrderViewSet, self).get_queryset().filter(order__user=self.request.user)


class AttributViewSet(viewsets.ModelViewSet):
    queryset = Attribut.objects.all()
    serializer_class = AttributSerializer


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

    def get_queryset(self):
        return super(MediaViewSet, self).get_queryset().filter(product__user=self.request.user)


class AttributDetailsViewSet(viewsets.ModelViewSet):
    queryset = AttributDetails.objects.all()
    serializer_class = AttributDetailsSerializer


class ProductAttributViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribut.objects.all()
    serializer_class = ProductAttribut


class CategoryAttributeViewSet(viewsets.ModelViewSet):
    queryset = CategoryAttribute.objects.all()
    serializer_class = CategoryAttributSerializer
