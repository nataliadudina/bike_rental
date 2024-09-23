from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ Только владелец может изменять и удалять свой профиль. """

    def has_permission(self, request, view):
        return request.user.id == view.get_object().id


class IsModerator(permissions.BasePermission):
    """
    Только модератор или суперпользователь может добавлять, редактировать или удалять информацию о велосипедах,
    а также видеть список пользователей.
    """

    def has_permission(self, request, view):
        return (
                request.user.groups.filter(name='moderators').exists() or
                request.user.is_superuser
        )


class IsOwnerOrModerator(IsModerator, IsOwner):
    """ Только владелец может видеть свой профиль. Модератор может видеть любой профиль. """

    def has_permission(self, request, view):
        return super().has_permission(request, view) or request.user.id == view.get_object().id
