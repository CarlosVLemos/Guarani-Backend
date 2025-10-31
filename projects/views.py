from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.utils import timezone

from .models import Project, Document
from .serializers import ProjectListSerializer, ProjectDetailSerializer, DocumentSerializer
from .permissions import IsProjectOwnerOrReadOnly
from .filters import ProjectFilter
from .pagination import StandardResultsSetPagination
from users.permissions import IsAuditor


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Projetos.

    - `list`: Retorna todos os projetos ativos (acesso público).
    - `retrieve`: Retorna os detalhes de um projeto (acesso público para projetos ativos).
    - `create`: Cria um novo projeto (requer autenticação e ser Ofertante).
    - `update/partial_update`: Atualiza um projeto (apenas o dono).
    - `destroy`: Deleta um projeto (apenas o dono).
    - `my`: Retorna os projetos do usuário logado.
    - `upload_document`: Adiciona um documento a um projeto.
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

    @action(
        detail=True, methods=["post"], url_path="documents",
        parser_classes=[MultiPartParser, FormParser]
    )
    def upload_document(self, request, pk=None):
        """Faz o upload de um documento para um projeto específico."""
        project = self.get_object()
        # A permissão IsProjectOwnerOrReadOnly já é checada para o objeto do projeto,
        # então não precisamos de outra verificação de permissão aqui.
        
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "Envie um arquivo no campo 'file'."}, status=status.HTTP_400_BAD_REQUEST)
        
        doc_name = request.data.get("name") or file_obj.name
        document = Document.objects.create(project=project, name=doc_name, file=file_obj)
        serializer = DocumentSerializer(document)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="validate", permission_classes=[IsAuthenticated, IsAuditor])
    def validate_project(self, request, pk=None):
        """Valida um projeto (ação reservada a usuários do grupo Auditor)."""
        project = self.get_object()

        if project.status == Project.Status.VALIDATED:
            return Response({"detail": "Projeto já está validado."}, status=status.HTTP_400_BAD_REQUEST)

        project.status = Project.Status.VALIDATED
        project.validated_by = request.user
        project.validated_at = timezone.now()
        project.save(update_fields=["status", "validated_by", "validated_at", "updated_at"])

        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="activate", permission_classes=[IsAuthenticated, IsProjectOwnerOrReadOnly])
    def activate_project(self, request, pk=None):
        """Ativa um projeto já VALIDATED (ação reservada ao dono do projeto)."""
        project = self.get_object()

        # Permissão a nível de objeto: somente o dono pode ativar
        if project.ofertante != request.user:
            return Response({"detail": "Apenas o ofertante pode ativar o projeto."}, status=status.HTTP_403_FORBIDDEN)

        if project.status != Project.Status.VALIDATED:
            return Response({"detail": "Somente projetos validados podem ser ativados."}, status=status.HTTP_400_BAD_REQUEST)

        project.status = Project.Status.ACTIVE
        project.save(update_fields=["status", "updated_at"])
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)