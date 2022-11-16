from django.contrib import admin
from .models import (
    City,
    Address,
    Governorate
)
# Register your models here.
from .views import AddressView

admin.site.register(City)
admin.site.register(Address)
admin.site.register(Governorate)
