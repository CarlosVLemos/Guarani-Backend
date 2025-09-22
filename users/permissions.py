# accounts/permissions.py
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite ações apenas se o request.user for staff (admin) ou o owner do objeto.
    Para BaseUser, owner é o próprio usuário (obj == request.user).
    Para modelos que têm atributo 'user', comparamos obj.user == request.user.
    """

    def has_object_permission(self, request, view, obj):
        # admin tem permissão full
        if request.user and request.user.is_staff:
            return True

        # caso obj seja user
        if isinstance(obj, User):
            return obj == request.user

        # caso obj tenha atributo 'user'
        target_user = getattr(obj, "user", None)
        if target_user:
            return target_user == request.user

        # para segurança, negar por padrão
        return False