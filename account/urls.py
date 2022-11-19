from django.urls import path, include
from rest_framework import routers
from .views import PhoneNumberViewSet

router = routers.SimpleRouter()
router.register(r'phone', PhoneNumberViewSet)

urlpatterns = [
    path('', include(router.urls))
]
