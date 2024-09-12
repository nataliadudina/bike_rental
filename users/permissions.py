from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ Класс для ограничения прав доступа. Только владелец может просматривать и изменять свой профиль. """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
