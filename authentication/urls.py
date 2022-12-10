from django.urls import path, include
from rest_framework import routers
from .views import ChangePasswordView, UserCreateView, TokenCreateView, UserViewSet, ReviewViewSet, WishListViewSet

router = routers.SimpleRouter()
router.register(r'user', UserViewSet, basename='users')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'wishlist', WishListViewSet, basename='wishlist')

urlpatterns = [
    path('password-change/', ChangePasswordView.as_view(), name='password-change'),
    path('user-creation/', UserCreateView.as_view(), name='user-creation'),
    path('login/', TokenCreateView.as_view(), name='user-login'),
    path('', include(router.urls))
]
