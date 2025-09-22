from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProjectOwnerOrReadOnly(BasePermission):
    """
    Permissão personalizada para permitir que apenas os donos de um projeto o editem.
    - Qualquer usuário (autenticado ou não) pode visualizar (GET, HEAD, OPTIONS).
    - Apenas o 'ofertante' (dono) do projeto pode modificar (PUT, PATCH, DELETE).
    """

    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer requisição,
        # então sempre permitiremos requisições GET, HEAD ou OPTIONS.
        if request.method in SAFE_METHODS:
            return True

        # Permissões de escrita são permitidas apenas para o dono do projeto.
        # O `obj` aqui é a instância do modelo `Project`.
        return obj.ofertante == request.user