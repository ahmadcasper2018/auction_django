from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'shipping-company', views.ShippingCompanyViewSet, basename='shipping-company')
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'product-order', views.ProductOrderViewSet, basename='product-order')
urlpatterns = [
    path('', include(router.urls))
]

print(router.urls)
