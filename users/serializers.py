from rest_framework import serializers
from .validators import validate_file_type_and_size
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import (
    OfertanteProfile, OfertanteDocument,
    CompradorProfile, CompradorOrganization,
    CompradorRequirements, CompradorDocuments
)

User = get_user_model()


# --- Serializers para Ofertante ---

class OfertanteProfileSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do Ofertante."""
    class Meta:
        model = OfertanteProfile
        # Exclui o usuário, pois ele será associado automaticamente
        exclude = ['user']


class OfertanteDocumentSerializer(serializers.ModelSerializer):
    """Serializer para os documentos do Ofertante."""
    class Meta:
        model = OfertanteDocument
        exclude = ['user']
        extra_kwargs = {
            'file': {'validators': [validate_file_type_and_size]}
        }


# --- Serializers para Comprador ---

class CompradorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompradorProfile
        exclude = ['user']

class CompradorOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompradorOrganization
        exclude = ['user']

class CompradorRequirementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompradorRequirements
        exclude = ['user']

class CompradorDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompradorDocuments
        exclude = ['user']
        extra_kwargs = {
            'file': {'validators': [validate_file_type_and_size]}
        }


# --- Serializers de Usuário (Base e Registro) ---

class BaseUserSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de usuário base."""
    class Meta:
        model = User
        fields = [
            "id", "email", "user_type",
            "is_active", "is_verified", "verification_status",
            "created_at", "updated_at", "last_login",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_login"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar um novo usuário.
    Aceita dados aninhados para o perfil de Ofertante.
    O perfil de Comprador é mais complexo e deve ser preenchido em etapas posteriores.
    """
    ofertante_profile = OfertanteProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'user_type', 'ofertante_profile']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
        }

    def validate(self, data):
        user_type = data.get('user_type')
        profile_data = data.get('ofertante_profile')

        if user_type == 'OFERTANTE' and not profile_data:
            raise serializers.ValidationError(
                "O perfil do ofertante (`ofertante_profile`) é obrigatório para usuários do tipo OFERTANTE."
            )
        if user_type == 'COMPRADOR' and profile_data:
            raise serializers.ValidationError(
                "O perfil de ofertante não deve ser fornecido para usuários do tipo COMPRADOR."
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('ofertante_profile', None)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )

        if validated_data['user_type'] == 'OFERTANTE' and profile_data:
            OfertanteProfile.objects.create(user=user, **profile_data)
        
        # Para Compradores, o perfil é criado em um passo separado

        return user


# --- Serializer para /me ---
class UserMeSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    is_auditor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "user_type",
            "is_active",
            "is_verified",
            "verification_status",
            "is_staff",
            "is_superuser",
            "groups",
            "is_auditor",
            "created_at",
            "updated_at",
            "last_login",
        ]
        read_only_fields = fields

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def get_is_auditor(self, obj):
        return obj.groups.filter(name__iexact='auditor').exists()