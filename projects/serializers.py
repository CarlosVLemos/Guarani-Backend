from rest_framework import serializers
from .models import Project
from users.models import User # Importamos o User para obter o nome da organização

class OfertanteInfoSerializer(serializers.ModelSerializer):
    """Serializer simples para mostrar informações do Ofertante."""
    organization_name = serializers.CharField(source='ofertante_profile.organization_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'organization_name']

class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer para a listagem pública de projetos."""
    ofertante = OfertanteInfoSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'project_type',
            'status',
            'carbon_credits_available',
            'price_per_credit',
            'location',
            'ofertante',
            'created_at'
        ]

class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes, criação e atualização de um projeto."""
    ofertante = OfertanteInfoSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'ofertante', 'status', 'created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        """Associa o usuário logado como o ofertante do projeto."""
        validated_data['ofertante'] = self.context['request'].user
        return super().create(validated_data)