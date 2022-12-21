from rest_framework import routers, viewsets
from django.urls import path, include
from . import views
from authentication.views import WalletViewSet

router = routers.SimpleRouter()
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'brand', views.BrandViewSet, basename='brand')
router.register(r'shipping-company', views.ShippingCompanyViewSet, basename='shipping-company')
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'product-order', views.ProductOrderViewSet, basename='product-order')
router.register(r'attribute', views.AttributViewSet, basename='attribute')
router.register(r'auction-request', views.AuctionOrderRequestViewSet, basename='auction-request')
router.register(r'product-media', views.MediaViewSet, basename='product-media')
router.register(r'slider-media', views.SliderMediaViewSet, basename='slider-media')
router.register(r'slider', views.SliderViewSet, basename='slider')
router.register(r'product-values', views.ProductValuesViewset, basename='product-values')
router.register(r'page', views.PageViewSet)
router.register(r'logo', views.LogoViewSet)
attrs_router = routers.SimpleRouter()
attrs_router.register(r'product', views.ProductViewSet, basename='product')
attrs_router.register(r'category', views.CategoryAttributeViewSet, basename='category-attrs')
attrs_router.register(r'product', views.ProductAttributViewSet, basename='product-attribut')
attrs_router.register(r'detail', views.AttributDetailsViewSet, basename='attrs-details')

urlpatterns = [
    path('', include(router.urls)),
    path('attrs/', include(attrs_router.urls)),
]
