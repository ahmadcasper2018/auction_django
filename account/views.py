from django.shortcuts import render
from rest_framework import viewsets
from .models import Phone
from .serializers import PhoneNumberSerializer


# Create your views here.

class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = Phone.objects.all()
    serializer_class = PhoneNumberSerializer
