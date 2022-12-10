from django.contrib import admin

from .models import User, Phone, Review, WishList

# Register your models here.


admin.site.register(User)
admin.site.register(Phone)
admin.site.register(Review)
admin.site.register(WishList)


