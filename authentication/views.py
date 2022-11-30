from rest_framework import viewsets
from .models import Phone
from .serializers import PhoneNumberSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


# class FaceBookLoginView(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client


# Create your views here.

class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = Phone.objects.all()
    serializer_class = PhoneNumberSerializer

    def get_queryset(self):
        return super(PhoneNumberViewSet, self).get_queryset().filter(user=self.request.user)
