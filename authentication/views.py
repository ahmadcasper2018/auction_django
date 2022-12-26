from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView, get_object_or_404
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


class ActionViewMixin(object):
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            data = {'message': 'You have entered wrong email or password',
                    'errors': {'email or password': serializer.errors.get('non_field_errors')}}

            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        return self._action(serializer)


class TokenCreateView(ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """

    serializer_class = settings.SERIALIZERS.token_create
    permission_classes = settings.PERMISSIONS.token_create

    def _action(self, serializer):
        token_data = get_tokens_for_user(serializer.user)
        response = {}
        extra_data = UserDetailSerializer(serializer.user)
        response.update({'id': serializer.user.id})
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
        errors = {"message": "Errors with the entered data for this user"}
        if not serializer.is_valid():
            errors.update({'errors': serializer.errors})
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        response = {}
        response.update({'id': data.get('id')})
        response.update({'user': data})
        refresh = RefreshToken.for_user(request.user)
        if self.request.user and not (self.request.user.is_superuser or self.request.user.is_staff):
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
        user_types = self.request.query_params.get('user_types', None)
        qs = super(UserViewSet, self).get_queryset()
        superusers = qs.none()
        admins = qs.none()
        normal = qs.none()
        if user_types:
            types = user_types.split(',')
            if user.is_superuser:
                if 'superuser' in types:
                    superusers = qs.filter(is_superuser=True)
                if 'admin' in types:
                    admins = qs.filter(is_staff=True)
            if 'normal' in types:
                normal = qs.filter(is_staff=False, is_superuser=False)
            qs = superusers | admins | normal
        if user.is_staff and not user.is_superuser:
            qs = qs.filter(is_superuser=False, is_staff=False)
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(pk=user.pk)
        return qs


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (ReviewPermession,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        qs = super(ReviewViewSet, self).get_queryset()
        product = self.request.query_params.get('product')
        if product:
            qs = qs.filter(product__pk=product)
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
            product = get_object_or_404(Product, pk=obj)
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


class WalletLogView(viewsets.ReadOnlyModelViewSet):
    queryset = WalletLog.objects.all()
    serializer_class = WalletSerializer

    def get_queryset(self):
        user = self.request.user
        user_filter = self.request.query_params.get('user')
        qs = super(WalletLogView, self).get_queryset()
        if (user.is_superuser or user.is_staff) and user_filter:
            qs = qs.filter(wallet__userpk=user_filter)
        if not (user.is_superuser or user.is_staff):
            return qs.filter(wallet__user=user)
        return qs
