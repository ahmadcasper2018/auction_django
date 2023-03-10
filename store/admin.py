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
    Brand, SliderMedia, Slider, AuctionOrder, AttributValue, Page, CategoryAttribute

)

# Register your models here.
admin.site.register(Attribut)
admin.site.register(Category)
admin.site.register(AttributDetails)

admin.site.register(Product)
admin.site.register(ProductAttribut)
admin.site.register(Media)
admin.site.register(Order)
admin.site.register(ProductOrder)
admin.site.register(ShippingCompany)
admin.site.register(Brand)
admin.site.register(SliderMedia)
admin.site.register(AuctionOrder)
admin.site.register(Slider)
admin.site.register(AttributValue)
admin.site.register(Page)
admin.site.register(CategoryAttribute)

