from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Предоставляет права на выполнение запросов
    только суперпользователю и администратору.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)


class AnonimReadOnly(permissions.BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsSuperUserIsAdminIsModeratorIsAuthor(permissions.BasePermission):
    """
    Разрешает анонимному пользователю только безопасные запросы.
    Доступ к запросам PATCH и DELETE предоставляется только
    суперпользователю, администратору, аутентифицированным пользователям
    с ролью admin или moderator, и автору.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                request.user.is_admin
                or request.user.is_moderator
                or request.user == obj.author
            )
        return False
