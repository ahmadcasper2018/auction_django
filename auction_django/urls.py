"""auction_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from authentication.views import GoogleLoginView
from allauth.socialaccount.providers.google import views as google_views

from django.views import View
from django.http import JsonResponse, HttpResponse


def index(request):
    return HttpResponse(status=200)


# class RedirectSocial(View):
#
#     def get(self, request, *args, **kwargs):
#         code, state = str(request.GET['code']), str(request.GET['state'])
#         json_obj = {'code': code, 'state': state}
#         print(json_obj)
#         return JsonResponse(json_obj)
#

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('location/', include('location.urls')),
    path('phone/', include('authentication.urls')),
    # path(r'test/', include('djoser.social.urls')),
    path('accounts/', include('allauth.urls')),
    # path('accounts/profile/', RedirectSocial.as_view()),
    path('store/', include('store.urls')),
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('rest-auth/google/', GoogleLoginView.as_view()),
    path('', index),
    path('general/', include('general.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
