from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from django.db import transaction

from .models import Transaction
from .serializers import TransactionSerializer, PublicTransactionSerializer
from projects.models import Project # Precisamos do modelo Project para pegar o preço

class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet para criar e listar transações.
    - POST: Cria uma nova transação (compra de créditos).
    - GET: Lista as transações do usuário logado.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Esta view deve retornar uma lista de todas as transações
        para o usuário autenticado atualmente.
        """
        return Transaction.objects.filter(buyer=self.request.user).select_related('project', 'buyer')

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Lógica customizada para criar uma transação.
        """
        project = serializer.validated_data['project']
        quantity = serializer.validated_data['quantity']

        # 1. Pega o preço atual do crédito do projeto.
        #    (Estou assumindo que seu modelo Project tem um campo 'price_per_credit')
        try:
            current_price_per_credit = project.price_per_credit
        except AttributeError:
            # Se o campo não existir, retorna um erro claro.
            # Você precisará adicionar o campo `price_per_credit` ao seu modelo `projects.Project`
            raise serializers.ValidationError(
                {"detail": "O modelo de Projeto não possui um atributo 'price_per_credit'."}
            )

        # 2. Calcula o preço total.
        total_price = current_price_per_credit * quantity

        # 3. TODO: Adicionar sua lógica de verificação de saldo do usuário aqui.
        #    Ex: if self.request.user.profile.balance < total_price:
        #            raise serializers.ValidationError("Saldo insuficiente.")

        # 4. TODO: Adicionar sua lógica para debitar o saldo do usuário aqui.
        #    Ex: self.request.user.profile.balance -= total_price
        #        self.request.user.profile.save()

        # 5. Salva a transação com os dados calculados e o comprador.
        serializer.save(
            buyer=self.request.user,
            price_per_credit_at_purchase=current_price_per_credit,
            total_price=total_price
        )

        # 6. TODO: Adicionar lógica para creditar os créditos ao projeto/vendedor (se aplicável).


class PublicTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para a visualização pública de transações.
    - GET: Lista todas as transações de forma anônima.
    """
    queryset = Transaction.objects.all().select_related('project')
    serializer_class = PublicTransactionSerializer
    permission_classes = [permissions.AllowAny]
