from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from djoser import utils

from djoser.conf import settings

from store.models import Product
from store.permessions import WalletPermession
from .permessions import UserPermession, ReviewPermession, WishListPermession

from .models import (
    Phone,
    User,
    Wallet,
    Review,
    WishList, WalletLog
)
from .serializers import (
    PhoneNumberSerializer,
    ChangePasswordSerializer,
    UserCreationSerializer,
    UserDetailSerializer,
    WalletSerializer,
    UserExtendedSerializer,
    ReviewSerializer,
    WishListSerializer
)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


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


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = (WalletPermession,)

    def get_queryset(self):
        return super(WalletViewSet, self).get_queryset().filter(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserExtendedSerializer
    queryset = User.objects.all()
    permission_classes = (UserPermession,)

    def create(self, request, *args, **kwargs):
        serializer = UserCreationSerializer(data=request.data, context={"request": self.request})
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

    # def update(self, request, pk=None):
    #     obj = User.objects.get(pk=pk)
    #     serializer = self.serializer_class(instance=obj, data=request.data, partial=True, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(status=status.HTTP_202_ACCEPTED, data=serializer.data)

    def get_queryset(self):
        user = self.request.user
        qs = super(UserViewSet, self).get_queryset()
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(pk=user.pk)
        return qs


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (IsAuthenticated, ReviewPermession)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        qs = super(ReviewViewSet, self).get_queryset()
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)
        return qs


class WishListViewSet(viewsets.ModelViewSet):
    serializer_class = WishListSerializer
    queryset = WishList.objects.all()
    permission_classes = (IsAuthenticated, WishListPermession)

    @action(detail=False, methods=['delete'])
    def remove_list(self, request):
        objs = request.data['objects']
        for obj in objs:
            WishList.objects.get(pk=obj).delete()
        return Response(status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        objs = request.data['objects']
        news_objs = []
        for obj in objs:
            product = Product.objects.get(pk=obj)
            new_wish = WishList.objects.create(user=user, product=product)
            news_objs.append(
                new_wish
            )
            user.wishlist.add(new_wish)
            user.save()
        serializer = self.serializer_class(news_objs, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = super(WishListViewSet, self).get_queryset()
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)
        return qs


class WalletLogView(viewsets.ModelViewSet):
    queryset = WalletLog.objects.all()
    serializer_class = WalletSerializer
