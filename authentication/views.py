import gender as gender
from djoser.serializers import UserSerializer
from rest_framework import viewsets, generics, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework import generics

from djoser import utils

from djoser.conf import settings

from store.permessions import WalletPermession
from .permessions import UserPermession

User = get_user_model()

from .models import Phone, User, Wallet
from .serializers import PhoneNumberSerializer, ChangePasswordSerializer, UserCreationSerializer, UserDetailSerializer, \
    WalletSerializer, UserExtendedSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class UserCreateView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        response = {}
        response.update({'user': data})
        refresh = RefreshToken.for_user(request.user)
        response.update({'refresh': str(refresh)})
        response.update({'access': str(refresh.access_token)})
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)


# class FaceBookLoginView(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequest(APIView):
    def get(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')
        response = {
            "uid": uid,
            "reset token": token
        }
        return Response(response, status=200)


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token_data = get_tokens_for_user(serializer.user)
        response = {}
        extra_data = UserDetailSerializer(serializer.user)
        response.update({'user': extra_data.data})
        response.update(token_data)
        return Response(
            response, status=status.HTTP_200_OK
        )


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = (WalletPermession,)

    def get_queryset(self):
        return super(WalletViewSet, self).get_queryset().filter(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserExtendedSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, UserPermession)

    def update(self, request, pk=None):
        obj = User.objects.get(pk=pk)
        serializer = self.serializer_class(instance=obj, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED, data=serializer.data)

    def get_queryset(self):
        user = self.request.user
        qs = super(UserViewSet, self).get_queryset()
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(pk=user.pk)
        return qs
