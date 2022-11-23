from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'shipping-company', views.ShippingCompanyViewSet, basename='shipping-company')
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'product-order', views.ProductOrderViewSet, basename='product-order')
router.register(r'attribute', views.AttributViewSet, basename='attribute')

router.register(r'product-media', views.MediaViewSet, basename='product-media')

attrs_router = routers.SimpleRouter()
attrs_router.register(r'product', views.ProductViewSet, basename='product')
attrs_router.register(r'category', views.CategoryAttributeViewSet, basename='category-attrs')
attrs_router.register(r'product', views.ProductAttributViewSet, basename='product-attribut')
attrs_router.register(r'detail', views.AttributDetailsViewSet, basename='attrs-details')

urlpatterns = [
    path('', include(router.urls)),
    path('attrs/', include(attrs_router.urls))
]

print(router.urls)
