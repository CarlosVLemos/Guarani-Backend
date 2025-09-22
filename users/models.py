import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Nosso Modelo de Usuário customizado
# -----------------------------------------------------------------------------
class User(AbstractUser):
    """
    Modelo de usuário base para toda a plataforma.
    """
    class UserType(models.TextChoices):
        OFERTANTE = 'OFERTANTE', 'Ofertante'
        COMPRADOR = 'COMPRADOR', 'Comprador'

    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        APPROVED = 'APPROVED', 'Aprovado'
        REJECTED = 'REJECTED', 'Rejeitado'

    username = None
    first_name = None
    last_name = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('endereço de e-mail', unique=True, help_text="O e-mail será usado para login.")
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        verbose_name='tipo de usuário'
    )
    is_verified = models.BooleanField(default=False, verbose_name='verificado')
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        verbose_name='status da verificação'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']

    def __str__(self):
        return self.email


# 2. Modelos de Perfil para Ofertantes
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ofertante_profile')

    contact_name = models.CharField(max_length=255, verbose_name="Nome do Contato")
    contact_position = models.CharField(max_length=100, verbose_name="Cargo do Contato")
    phone = models.CharField(max_length=20, verbose_name="Telefone")
    organization_type = models.CharField(max_length=30, choices=OrganizationType.choices, verbose_name="Tipo de Organização")
    organization_name = models.CharField(max_length=255, verbose_name="Nome da Organização")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name='CNPJ')
    website = models.URLField(blank=True, verbose_name="Website")
    description = models.TextField(blank=True, verbose_name="Descrição (Missão/Visão)")

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ofertante_documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, verbose_name="Tipo de Documento")
    file = models.FileField(upload_to='ofertante_documents/%Y/%m/%d/', verbose_name="Arquivo")
    expiration_date = models.DateField(null=True, blank=True, verbose_name="Data de Expiração")
    verified = models.BooleanField(default=False, verbose_name="Verificado")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} de {self.user.email}"