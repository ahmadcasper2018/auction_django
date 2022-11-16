from rest_framework import routers
from django.urls import path, include
from .views import (
    CityView,
    AddressView,
    GovernorateView,
)

router = routers.SimpleRouter()
router.register(r'city', CityView)
router.register(r'address', AddressView)
router.register(r'governorate', GovernorateView)

urlpatterns = [
    path('', include(router.urls))
]
