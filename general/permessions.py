from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff)


class SettingsAccress(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))
