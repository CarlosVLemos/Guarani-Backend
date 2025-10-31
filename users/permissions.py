# accounts/permissions.py
from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

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


class IsAuditor(permissions.BasePermission):
    """
    Permite acesso apenas a usuários que pertençam ao grupo 'auditor' (case-insensitive)
    ou que sejam staff/superuser.

    Uso típico: restringir ações de validação/aprovação a auditores.
    """

    AUDITOR_GROUP_NAME = "auditor"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or getattr(user, "is_superuser", False):
            return True

        # Checa pertinência ao grupo 'auditor'
        return user.groups.filter(name__iexact=self.AUDITOR_GROUP_NAME).exists()