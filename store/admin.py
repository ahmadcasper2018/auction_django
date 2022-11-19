from django.contrib import admin
from .models import (
    AttributDetails,
    ProductAttribut,
    Category,
    Attribut,
    Product,
    ShippingCompany,
    Media,
    Order,
    ProductOrder,

)

# Register your models here.
admin.site.register(Attribut)
admin.site.register(AttributDetails)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductAttribut)
admin.site.register(ShippingCompany)
admin.site.register(Media)
admin.site.register(Order)
admin.site.register(ProductOrder)

