from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Project
from .serializers import ProjectListSerializer, ProjectDetailSerializer
from .permissions import IsProjectOwnerOrReadOnly
from .filters import ProjectFilter
from .pagination import StandardResultsSetPagination


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Projetos.

    - `list`: Retorna todos os projetos ativos (acesso público).
    - `retrieve`: Retorna os detalhes de um projeto (acesso público para projetos ativos).
    - `create`: Cria um novo projeto (requer autenticação e ser Ofertante).
    - `update/partial_update`: Atualiza um projeto (apenas o dono).
    - `destroy`: Deleta um projeto (apenas o dono).
    - `my`: Retorna os projetos do usuário logado.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsProjectOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProjectFilter
    ordering_fields = ["created_at", "price_per_credit", "carbon_credits_available", "name"]
    search_fields = ["name", "description", "location", "project_type"]

    def get_queryset(self):
        user = self.request.user
        # Para a ação 'list', mostramos apenas projetos ativos a todos.
        if self.action == 'list':
            return Project.objects.alive().filter(status=Project.Status.ACTIVE)
        
        # Se o usuário não estiver autenticado, ele só pode ver projetos ativos.
        if not user.is_authenticated:
            return Project.objects.alive().filter(status=Project.Status.ACTIVE)

        # Usuários autenticados (donos ou não) podem ver projetos em outros status
        # A permissão IsProjectOwnerOrReadOnly cuidará do acesso de escrita.
        return Project.objects.alive()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'my':
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        # Associa o usuário logado como o ofertante do projeto.
        serializer.save(ofertante=self.request.user)

    def perform_destroy(self, instance):
        # Usa soft delete em vez de apagar o registro do banco.
        instance.soft_delete()

    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        """Retorna todos os projetos pertencentes ao usuário autenticado."""
        if not request.user.is_authenticated:
            return Response({"detail": "Autenticação requerida."}, status=status.HTTP_401_UNAUTHORIZED)
        
        qs = Project.objects.alive().filter(ofertante=request.user)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page or qs, many=True)
        
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    # TODO: Implementar upload de documentos com as devidas validações e serializers.
    # A ação de upload de documentos foi removida temporariamente para simplificação.
