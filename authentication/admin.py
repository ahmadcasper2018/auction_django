from django.contrib import admin
from social_core.backends import username

from .models import User, Phone


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active')
    fields = ['_all__']


admin.site.register(User, UserAdmin)
admin.site.register(Phone)
