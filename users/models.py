import uuid
import re
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)

# -------------------------
# Validação de CNPJ (Helper function)
# -------------------------
def validate_cnpj(value: str):
    """
    Validação completa de CNPJ (formato + dígitos verificadores).
    Aceita entradas com ou sem pontuação.
    Levanta django.core.exceptions.ValidationError quando inválido.
    """
    if not value:
        raise ValidationError("CNPJ é obrigatório.")
    digits = re.sub(r'\D', '', value)
    if len(digits) != 14:
        raise ValidationError("CNPJ inválido: deve conter 14 dígitos.")
    if digits == digits[0] * 14:
        raise ValidationError("CNPJ inválido.")

    def calc_digit(digs, multipliers):
        total = 0
        for d, m in zip(digs, multipliers):
            total += int(d) * m
        rest = total % 11
        return '0' if rest < 2 else str(11 - rest)

    base12 = digits[:12]
    mult1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    dv1 = calc_digit(base12, mult1)
    base13 = base12 + dv1
    mult2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    dv2 = calc_digit(base13, mult2)

    if digits[-2:] != dv1 + dv2:
        raise ValidationError("CNPJ inválido (dígitos verificadores não conferem).")


# -------------------------
# User manager
# -------------------------
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("O e-mail deve ser informado")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
            user.password_hash = user.password
        else:
            user.password_hash = ""
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


# -------------------------
# Modelo de Usuário Unificado
# -------------------------
class BaseUser(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        OFERTANTE = "OFERTANTE", "Ofertante"
        COMPRADOR = "COMPRADOR", "Comprador"

    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        APPROVED = "APPROVED", "Aprovado"
        REJECTED = "REJECTED", "Rejeitado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('endereço de e-mail', unique=True, help_text="O e-mail será usado para login.")
    password_hash = models.CharField(max_length=128, blank=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        verbose_name='tipo de usuário'
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, verbose_name='verificado')
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        verbose_name='status da verificação'
    )
    wallet_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=1000000.00, 
        verbose_name='Saldo da Carteira (R$)'
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['user_type']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.password:
            self.password_hash = self.password
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


# -----------------------------------------------------------------------------
# Modelos de Perfil para Ofertantes
# -----------------------------------------------------------------------------
class OfertanteProfile(models.Model):
    """
    Perfil detalhado para usuários do tipo Ofertante.
    """
    class OrganizationType(models.TextChoices):
        ONG = 'ONG', 'ONG'
        EMPRESA_PRIVADA = 'EMPRESA_PRIVADA', 'Empresa Privada'
        COOPERATIVA = 'COOPERATIVA', 'Cooperativa'
        PROJETO_INDEPENDENTE = 'PROJETO_INDEPENDENTE', 'Projeto Independente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ofertante_profile')

    contact_name = models.CharField(max_length=255, verbose_name="Nome do Contato")
    contact_position = models.CharField(max_length=100, verbose_name="Cargo do Contato")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    organization_type = models.CharField(max_length=30, choices=OrganizationType.choices, verbose_name="Tipo de Organização")
    organization_name = models.CharField(max_length=255, verbose_name="Nome da Organização")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name='CNPJ')
    website = models.URLField(blank=True, verbose_name="Website")
    description = models.TextField(blank=True, verbose_name="Descrição (Missão/Visão)")

    def clean(self):
        if getattr(self.user, "user_type", None) != BaseUser.UserType.OFERTANTE:
            raise ValidationError("Perfil de Ofertante só pode ser associado a um usuário com user_type='OFERTANTE'.")

    def __str__(self):
        return f"Perfil de Ofertante: {self.organization_name or self.contact_name}"

class OfertanteDocument(models.Model):
    """
    Documentos para usuários do tipo Ofertante.
    """
    class DocumentType(models.TextChoices):
        ESTATUTO_SOCIAL = 'ESTATUTO_SOCIAL', 'Estatuto Social'
        LICENCA_AMBIENTAL = 'LICENCA_AMBIENTAL', 'Licença Ambiental'
        CERTIFICACAO_TECNICA = 'CERTIFICACAO_TECNICA', 'Certificação Técnica'
        COMPROVANTE_ATIVIDADE = 'COMPROVANTE_ATIVIDADE', 'Comprovante de Atividade'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ofertante_documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, verbose_name="Tipo de Documento")
    file = models.FileField(upload_to='ofertante_documents/%Y/%m/%d/', verbose_name="Arquivo")
    expiration_date = models.DateField(null=True, blank=True, verbose_name="Data de Expiração")
    verified = models.BooleanField(default=False, verbose_name="Verificado")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if getattr(self.user, "user_type", None) != BaseUser.UserType.OFERTANTE:
            raise ValidationError("Documento de Ofertante só pode ser associado a um usuário com user_type='OFERTANTE'.")

    def __str__(self):
        return f"{self.get_document_type_display()} de {self.user.email}"


# -------------------------
# MODELOS: COMPRADORES
# -------------------------
class CompradorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comprador_profile")
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_position = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50)
    internal_code = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        if getattr(self.user, "user_type", None) != BaseUser.UserType.COMPRADOR:
            raise ValidationError("Profile de Comprador só pode ser associado a um BaseUser com user_type='COMPRADOR'.")

    def __str__(self):
        return f"CompradorProfile: {self.user.email}"


class CompradorOrganization(models.Model):
    class IndustrySector(models.TextChoices):
        MINERACAO = "MINERACAO", "Mineração"
        PETROLEO = "PETROLEO", "Petróleo"
        SIDERURGIA = "SIDERURGIA", "Siderurgia"
        BANCARIO = "BANCARIO", "Bancário"
        MANUFATURA = "MANUFATURA", "Manufatura"
        OUTROS = "OUTROS", "Outros"

    class CompanySize(models.TextChoices):
        PEQUENA = "PEQUENA", "Pequena"
        MEDIA = "MEDIA", "Média"
        GRANDE = "GRANDE", "Grande"
        MULTINACIONAL = "MULTINACIONAL", "Multinacional"

    class RevenueRange(models.TextChoices):
        MENOS_50M = "MENOS_50M", "Menos_50M"
        _50M_500M = "50M_500M", "50M-500M"
        _500M_2B = "500M_2B", "500M-2B"
        MAIS_2B = "MAIS_2B", "Mais_2B"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comprador_organization")
    company_name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=20, unique=True, validators=[validate_cnpj])
    industry_sector = models.CharField(max_length=50, choices=IndustrySector.choices, default=IndustrySector.OUTROS)
    company_size = models.CharField(max_length=20, choices=CompanySize.choices, blank=True, null=True)
    is_publicly_traded = models.BooleanField(default=False)
    stock_ticker = models.CharField(max_length=20, blank=True, null=True)
    annual_revenue = models.CharField(max_length=20, choices=RevenueRange.choices, blank=True, null=True)
    employees_count = models.PositiveIntegerField(blank=True, null=True)
    esg_rating = models.CharField(max_length=50, blank=True, null=True)
    carbon_commitment = models.TextField(blank=True, null=True)
    website = models.URLField()
    linkedin = models.URLField(blank=True, null=True)

    def clean(self):
        if getattr(self.user, "user_type", None) != BaseUser.UserType.COMPRADOR:
            raise ValidationError("Organization de Comprador só pode ser associado a um BaseUser com user_type='COMPRADOR'.")
        if self.is_publicly_traded and not self.stock_ticker:
            raise ValidationError("Se is_publicly_traded=True, stock_ticker deve ser informado.")

    def __str__(self):
        return self.company_name


class CompradorRequirements(models.Model):
    class BudgetRange(models.TextChoices):
        ATE_50K = "ATE_50K", "Até 50K"
        _50K_200K = "50K_200K", "50K-200K"
        _200K_1M = "200K_1M", "200K-1M"
        MAIS_1M = "MAIS_1M", "Mais 1M"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comprador_requirements")
    annual_carbon_target = models.PositiveIntegerField()
    compensation_deadline = models.DateField()
    preferred_regions = models.JSONField(default=list, blank=True)
    preferred_project_types = models.JSONField(default=list, blank=True)
    required_certifications = models.JSONField(default=list, blank=True)
    min_project_volume = models.PositiveIntegerField(blank=True, null=True)
    max_project_volume = models.PositiveIntegerField(blank=True, null=True)
    budget_range = models.CharField(max_length=20, choices=BudgetRange.choices, blank=True, null=True)
    additionality_requirements = models.BooleanField(default=False)
    vintage_preference = models.PositiveIntegerField(blank=True, null=True)

    def clean(self):
        if getattr(self.user, "user_type", None) != BaseUser.UserType.COMPRADOR:
            raise ValidationError("Requirements de Comprador só podem ser associados a user_type='COMPRADOR'.")
        if self.min_project_volume and self.max_project_volume and self.min_project_volume > self.max_project_volume:
            raise ValidationError("min_project_volume não pode ser maior que max_project_volume.")

    def __str__(self):
        return f"Requirements: {self.user.email}"


class CompradorDocuments(models.Model):
    class DocumentType(models.TextChoices):
        POLITICA_SUSTENTABILIDADE = "POLITICA_SUSTENTABILIDADE", "Política Sustentabilidade"
        RELATORIO_ESG = "RELATORIO_ESG", "Relatório ESG"
        COMPROMISSO_CARBONO = "COMPROMISSO_CARBONO", "Compromisso Carbono"
        CERTIFICACAO_ISO = "CERTIFICACAO_ISO", "Certificação ISO"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comprador_documents")
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="compradores/documents/")
    file_path = models.CharField(max_length=500, blank=True)
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        if getattr(self.user, "user_type", None) != BaseUser.UserType.COMPRADOR:
            raise ValidationError("Documento só pode ser associado a um Comprador.")

    def save(self, *args, **kwargs):
        if self.file and not self.file_name:
            self.file_name = getattr(self.file, "name", "")
        if self.file:
            self.file_path = getattr(self.file, "name", "")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.document_type} - {self.user.email}"
