from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Transaction.
    Lida com a criação e visualização de transações.
    """
    # Para leitura (visualização), mostra o email do comprador.
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    
    # Para leitura, mostra o nome do projeto.
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Transaction
        # Campos a serem usados pela API.
        fields = [
            'id',
            'buyer_email',  # Campo de leitura
            'project',      # Campo de escrita (recebe o ID do projeto)
            'project_name', # Campo de leitura
            'quantity',
            'price_per_credit_at_purchase',
            'total_price',
            'timestamp'
        ]
        
        # Configurações extras para os campos
        extra_kwargs = {
            # O campo 'project' é usado apenas para criar/atualizar (write_only).
            # Ele não será exibido na resposta da API, usamos 'project_name' para isso.
            'project': {'write_only': True},
            
            # Estes campos são definidos pelo sistema no momento da compra,
            # não pelo usuário, por isso são read_only.
            'price_per_credit_at_purchase': {'read_only': True},
            'total_price': {'read_only': True},
        }

    def validate_quantity(self, value):
        """
        Validação a nível de campo: garante que a quantidade seja positiva.
        """
        if value <= 0:
            raise serializers.ValidationError("A quantidade de créditos deve ser um número positivo.")
        return value


class PublicTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer para a visualização pública de transações.
    Expõe apenas dados não-sensíveis.
    """
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'project_name',
            'quantity',
            'price_per_credit_at_purchase',
            'total_price',
            'timestamp'
        ]
