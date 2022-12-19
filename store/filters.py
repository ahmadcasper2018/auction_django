from django_filters import rest_framework as filters
from .models import Product


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = ('category',
                  'stock',
                  'user',
                  'category',
                  'address',
                  'active',
                  'start_time',
                  'end_time',
                  'status',
                  'used',
                  'new',
                  'price',
                  'min_price',
                  'current_price',
                  )
