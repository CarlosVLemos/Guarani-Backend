from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Transaction.
    """
    list_display = ('id', 'buyer', 'project', 'quantity', 'total_price', 'timestamp')
    list_filter = ('timestamp', 'project')
    search_fields = ('id__iexact', 'buyer__email', 'project__name')
    ordering = ('-timestamp',)
    
    # Torna todos os campos somente leitura no painel de detalhes,
    # pois uma transação não deve ser alterada após a criação.
    readonly_fields = (
        'id', 
        'buyer', 
        'project', 
        'quantity', 
        'price_per_credit_at_purchase', 
        'total_price', 
        'timestamp'
    )

    def has_add_permission(self, request):
        # Desabilita o botão de "Adicionar" no admin,
        # forçando que as transações sejam criadas pela API.
        return False

    def has_delete_permission(self, request, obj=None):
        # Opcional: Desabilita a capacidade de deletar transações pelo admin.
        # É uma boa prática para manter o histórico.
        return False
