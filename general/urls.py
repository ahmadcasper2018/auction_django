from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'question', views.QuestionViewSet)
router.register(r'keyword', views.KeyWordViewSet)
urlpatterns = [
    path('', include(router.urls))
]
