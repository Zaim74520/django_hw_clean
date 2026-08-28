from rest_framework.permissions import SAFE_METHODS, BasePermission


class CollectPermission(BasePermission):
    """Чтение — всем. Создание/изменение/удаление — автору или админу."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff