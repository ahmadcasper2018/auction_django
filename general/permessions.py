from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff)
