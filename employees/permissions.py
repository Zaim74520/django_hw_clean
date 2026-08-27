from rest_framework.permissions import SAFE_METHODS, BasePermission


class EmployeePermission(BasePermission):
    """
    Единое разрешение для API сотрудников.

    - Посетитель (любой, даже без токена): может только читать (GET).
    - Смотритель (группа keepers): может менять рабочее место (PATCH workplace).
    - Администратор (is_staff): может всё (CRUD).
    """

    def has_permission(self, request, view):
        # Чтение — разрешено всем
        if request.method in SAFE_METHODS:
            return True

        # Запись — только для авторизованных
        if not request.user.is_authenticated:
            return False

        # Админ может всё
        if request.user.is_staff:
            return True

        # Смотритель — только PATCH
        if (
            request.method == "PATCH"
            and request.user.groups.filter(name="keepers").exists()
        ):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Чтение — всем
        if request.method in SAFE_METHODS:
            return True

        # Админ может всё
        if request.user.is_authenticated and request.user.is_staff:
            return True

        # Смотритель — только смена рабочего места
        if (
            request.method == "PATCH"
            and request.user.is_authenticated
            and request.user.groups.filter(name="keepers").exists()
        ):
            if set(request.data.keys()) == {"workplace"}:
                return True

        return False