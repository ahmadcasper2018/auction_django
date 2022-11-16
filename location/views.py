from django.shortcuts import render
from rest_framework import viewsets
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

class CityView(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AddressView(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class GovernorateView(viewsets.ModelViewSet):
    queryset = Governorate.objects.all()
    serializer_class = GovernorateSerializer
