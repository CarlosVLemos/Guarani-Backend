
from rest_framework import serializers
from .models import User, OfertanteProfile
from django.db import transaction

class OfertanteProfileSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do Ofertante."""
    class Meta:
        model = OfertanteProfile
        fields = ['contact_name', 'contact_position', 'phone', 'organization_type', 'organization_name', 'cnpj', 'website', 'description']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para o registro de novos usuários, incluindo o perfil."""
    ofertante_profile = OfertanteProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'user_type', 'ofertante_profile']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def to_internal_value(self, data):
        """
        Move os dados do perfil de um formato plano para um aninhado, 
        permitindo que o Swagger envie os dados sem aninhamento explícito.
        """
        profile_data = {}
        profile_fields = [f.name for f in OfertanteProfile._meta.get_fields() if f.name not in ('id', 'user')]
        
        # Extrai os campos do perfil do nível superior dos dados
        for field in profile_fields:
            if field in data:
                profile_data[field] = data.pop(field)

        # Chama o método original
        internal_value = super().to_internal_value(data)
        
        # Adiciona os dados do perfil aninhados, se existirem
        if profile_data:
            internal_value['ofertante_profile'] = profile_data
            
        return internal_value

    def to_representation(self, instance):
        """Sobrescreve para incluir o perfil do ofertante na resposta."""
        representation = super().to_representation(instance)
        if hasattr(instance, 'ofertante_profile'):
            representation['ofertante_profile'] = OfertanteProfileSerializer(instance.ofertante_profile).data
        return representation

    def validate_user_type(self, value):
        """Garante que, por agora, apenas Ofertantes possam se registrar por esta view."""
        if value != 'OFERTANTE':
            raise serializers.ValidationError("No momento, o registro é permitido apenas para Ofertantes.")
        return value

    @transaction.atomic # Garante que ou tudo é criado, ou nada é
    def create(self, validated_data):
        profile_data = validated_data.pop('ofertante_profile', None)
        
        # Cria o usuário
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )

        # Cria o perfil do Ofertante se os dados foram fornecidos
        if profile_data:
            OfertanteProfile.objects.create(user=user, **profile_data)
        
        return user
