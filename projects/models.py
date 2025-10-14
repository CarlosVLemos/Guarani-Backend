import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ProjectQuerySet(models.QuerySet):
    def alive(self):
        """Retorna apenas os projetos que não foram deletados (soft delete).""" 
        return self.filter(is_deleted=False)

def document_upload_to(instance, filename):
    return f"projects/{instance.project.id}/{filename}"

class Project(models.Model):
    """Representa um projeto de crédito de carbono criado por um Ofertante."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        ACTIVE = "ACTIVE", "Ativo"
        VALIDATED = "VALIDATED", "Validado"
        COMPLETED = "COMPLETED", "Concluído"

    class ProjectType(models.TextChoices):
        REFLORESTAMENTO = "REFLORESTAMENTO", "Reflorestamento e Conservação"
        ENERGIA_RENOVAVEL = "ENERGIA_RENOVAVEL", "Energia Renovável"
        AGRICULTURA = "AGRICULTURA", "Agricultura de Baixo Carbono"
        GESTAO_RESIDUOS = "GESTAO_RESIDUOS", "Gestão de Resíduos"
        OUTRO = "OUTRO", "Outro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=180, verbose_name="Nome do Projeto")
    description = models.TextField(blank=True, verbose_name="Descrição Detalhada")
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        verbose_name="Tipo de Projeto"
    )
    location = models.CharField(max_length=180, blank=True, verbose_name="Localização (Cidade/Estado)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Longitude")

    carbon_credits_available = models.PositiveIntegerField(default=0, verbose_name="Créditos de Carbono Disponíveis")
    price_per_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Preço por Crédito (R$)")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, verbose_name="Status")

    ofertante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Evita apagar o projeto se o usuário for deletado
        related_name="projects",
        verbose_name="Ofertante Responsável"
    )

    is_deleted = models.BooleanField(default=False, verbose_name="Deletado")

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["project_type"]),
            models.Index(fields=["ofertante"]),
        ]
        ordering = ["-created_at"]

    def clean(self):
        """Garante que o dono do projeto é um Ofertante."""
        if self.ofertante and self.ofertante.user_type != 'OFERTANTE':
            raise ValidationError("O responsável pelo projeto deve ser um usuário do tipo 'Ofertante'.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Chama a validação do `clean()`
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def __str__(self):
        return self.name

class Document(models.Model):
    """Armazena documentos de verificação e relatórios de um projeto."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents", verbose_name="Projeto")
    name = models.CharField(max_length=180, verbose_name="Nome do Documento")
    file = models.FileField(upload_to=document_upload_to, verbose_name="Arquivo")
    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Data de Upload")

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name
