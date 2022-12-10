from rest_framework.permissions import BasePermission


class ProductPermession(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class WalletPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class BrandPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff
