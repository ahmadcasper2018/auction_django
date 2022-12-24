from rest_framework.permissions import BasePermission, SAFE_METHODS


class ProductPermession(BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PATCH', 'PUT']:
            return request.user.is_superuser or (request.user == obj.user)
        return True


class WalletPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class BrandPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff
