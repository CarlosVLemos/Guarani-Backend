
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Project, Document
from .serializers import ProjectSerializer, ProjectListSerializer, DocumentSerializer
from .permissions import IsOwnerForUnsafe
from .filters import ProjectFilter


ALLOWED_DOC_MIMES = {
    "application/pdf",
    "application/msword",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.alive()
    permission_classes = [IsOwnerForUnsafe]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProjectFilter
    ordering_fields = ["created_at", "price_per_credit", "carbon_credits_available", "name"]
    search_fields = ["name", "description", "location", "project_type"]

    def get_serializer_class(self):
        if self.action in ["list", "my"]:
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.alive()
        user = self.request.user

        # /api/projects/ → compradores veem apenas ACTIVE; staff vê tudo.
        if self.action in ["list"]:
            if user.is_authenticated and getattr(user, "is_staff", False):
                return qs
            return qs.filter(status=Project.Status.ACTIVE)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        if not (getattr(request.user, "is_staff", False) or obj.owner_id == getattr(request.user, "id", None)):
            if obj.status != Project.Status.ACTIVE:
                return Response({"detail": "Projeto indisponível."}, status=404)
        ser = self.get_serializer(obj)
        return Response(ser.data)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        obj.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="my")
    def my(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Autenticação requerida."}, status=401)
        qs = Project.objects.alive().filter(owner=request.user)
        page = self.paginate_queryset(qs)
        ser_class = self.get_serializer_class()
        ser = ser_class(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @action(
        detail=True, methods=["post"], url_path="documents",
        parser_classes=[MultiPartParser, FormParser]
    )
    def upload_document(self, request, pk=None):
        project = self.get_object()
        if not (getattr(request.user, "is_staff", False) or project.owner_id == getattr(request.user, "id", None)):
            return Response({"detail": "Sem permissão para anexar documentos."}, status=403)

        up = request.FILES.get("file")
        if not up:
            return Response({"detail": "Envie um arquivo em 'file'."}, status=400)

        ctype = getattr(up, "content_type", "")
        if ctype not in ALLOWED_DOC_MIMES:
            return Response({"detail": "Tipo de arquivo não permitido."}, status=400)

        name = request.data.get("name") or up.name
        doc = Document.objects.create(project=project, name=name, file=up)
        return Response(DocumentSerializer(doc).data, status=201)
