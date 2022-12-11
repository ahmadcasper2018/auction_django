from django.urls import path, include
from rest_framework import routers
from .views import (
    ChangePasswordView,
    TokenCreateView,
    UserViewSet,
    ReviewViewSet,
    WishListViewSet,
    WalletLogView,
    WalletViewSet
)

router = routers.SimpleRouter()
router.register(r'user', UserViewSet, basename='users')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'wishlist', WishListViewSet, basename='wishlist')
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'wallet-logs', WalletLogView, basename='wallet-logs')

urlpatterns = [
    path('password-change/', ChangePasswordView.as_view(), name='password-change'),
    # path('user-creation/', UserCreateView.as_view(), name='user-creation'),
    path('login/', TokenCreateView.as_view(), name='user-login'),
    path('', include(router.urls)),

]
