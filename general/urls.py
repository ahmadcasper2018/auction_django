from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'question', views.QuestionViewSet)
router.register(r'keyword', views.KeyWordViewSet)
router.register(r'settings', views.ContactSettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
