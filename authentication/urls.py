from django.urls import path, include
from rest_framework import routers
from .views import ChangePasswordView, UserCreateView

# router = routers.SimpleRouter()
# router.register(r'password-change', ChangePasswordView, basename='password-change')

urlpatterns = [
    path('password-change/', ChangePasswordView.as_view(), name='password-change'),
    path('user-creation/', UserCreateView.as_view(), name='user-creation'),
]
