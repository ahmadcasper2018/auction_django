from rest_framework.permissions import BasePermission


class UserPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff and request.user.is_superuser:
            return True
        elif request.user.pk == obj.pk:
            return True
        return False


class ReviewPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff and request.user.is_superuser:
            return True
        elif request.user == obj.user:
            return True
        return False


class WishListPermession(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
