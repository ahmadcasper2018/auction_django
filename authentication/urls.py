from django.urls import path, include
from rest_framework import routers
from .views import PhoneNumberViewSet

router = routers.SimpleRouter()
router.register(r'', PhoneNumberViewSet)

urlpatterns = [
    path('', include(router.urls))
]
