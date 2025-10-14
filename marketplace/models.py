import uuid
from django.db import models
from django.conf import settings


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buy_transactions", verbose_name="comprador")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="transactrions", verbose_name="Projeto")
    quantity = models.PositiveIntegerField(verbose_name="Quantidade de créditos")
    price_per_credit_at_purchase = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Preço por Crédito(no momento da compra)")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Preço Total da Transação")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data da Transação")


    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Transação {self.id} - {self.buyer.email} comprou {self.quantity} créditos de {self.project.name} por {self.total_price} em {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"