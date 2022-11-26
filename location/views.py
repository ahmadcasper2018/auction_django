from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from .serializers import (
    CitySerializer,
    AddressSerializer,
    GovernorateSerializer,
)
from .models import (
    City,
    Address,
    Governorate

)


# Create your views here.

class CityView(mixins.RetrieveModelMixin,
               mixins.ListModelMixin,
               mixins.UpdateModelMixin,
               viewsets.GenericViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AddressView(mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet,
                  ):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        return super(AddressView, self).get_queryset().filter(user=self.request.user)


class GovernorateView(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    queryset = Governorate.objects.all()
    serializer_class = GovernorateSerializer