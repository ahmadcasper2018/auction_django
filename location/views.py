from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
               mixins.CreateModelMixin,
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

    def get_queryset(self):
        qs = super(AddressView, self).get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs


class GovernorateView(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    queryset = Governorate.objects.all()
    serializer_class = GovernorateSerializer
