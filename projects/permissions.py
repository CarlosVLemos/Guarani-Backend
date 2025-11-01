from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuditor(BasePermission):
    """
    Permissão para verificar se o usuário é um auditor.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'AUDITOR'


class IsProjectOwnerOrReadOnly(BasePermission):
    """
    Permissão personalizada para permitir que apenas os donos de um projeto o editem.
    - Qualquer usuário (autenticado ou não) pode visualizar (GET, HEAD, OPTIONS).
    - Apenas o 'ofertante' (dono) do projeto ou um 'auditor' pode modificar (PUT, PATCH, DELETE).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        is_owner = obj.ofertante == request.user
        is_auditor = request.user.user_type == 'AUDITOR'

        return is_owner or is_auditor