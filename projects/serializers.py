from rest_framework import serializers
from .models import Project, Document
from users.models import BaseUser

# Serializer auxiliar para mostrar informações públicas do Ofertante
class OfertanteInfoSerializer(serializers.ModelSerializer):
    # Acessa o perfil do ofertante para pegar o nome da organização
    organization_name = serializers.CharField(source='ofertante_profile.organization_name', read_only=True)

    class Meta:
        model = BaseUser
        fields = ['id', 'organization_name']

# Serializer para os documentos do projeto
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "name", "file", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]

# Serializer para a listagem de projetos (campos públicos)
class ProjectListSerializer(serializers.ModelSerializer):
    ofertante = OfertanteInfoSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'image',
            'project_type',
            'status',
            'carbon_credits_available',
            'price_per_credit',
            'location',
            'ofertante',
            'created_at'
        ]

# Serializer para a visão detalhada de um projeto (todos os campos)
class ProjectDetailSerializer(serializers.ModelSerializer):
    ofertante = OfertanteInfoSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'id',
            'ofertante',
            'status',
            'validated_by',
            'validated_at',
            'created_at',
            'updated_at',
            'is_deleted'
        ]

    def validate(self, data):
        """ Adiciona validações customizadas. """
        lat = data.get("latitude")
        lon = data.get("longitude")
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError({"latitude": "Latitude deve estar entre -90 e 90."})
        if lon is not None and (lon < -180 or lon > 180):
            raise serializers.ValidationError({"longitude": "Longitude deve estar entre -180 e 180."})
        if data.get("price_per_credit", 0) < 0:
            raise serializers.ValidationError({"price_per_credit": "Preço não pode ser negativo."})
        return data

    def create(self, validated_data):
        """ Associa o usuário logado (que deve ser um Ofertante) como o dono do projeto. """
        user = self.context['request'].user
        if user.user_type != 'OFERTANTE':
            raise serializers.ValidationError("Apenas usuários do tipo 'Ofertante' podem criar projetos.")
        validated_data['ofertante'] = user
        return super().create(validated_data)
