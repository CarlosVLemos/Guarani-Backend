from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, PublicTransactionViewSet

# Define o namespace para estas URLs, útil para referenciá-las em outras partes do projeto.
app_name = 'marketplace'

# O DefaultRouter gera as URLs para o ViewSet automaticamente.
router = DefaultRouter()

# Registra o TransactionViewSet na rota 'transactions'.
# A URL será algo como /api/marketplace/transactions/
# basename é importante para garantir que os nomes das URLs geradas sejam únicos.
router.register(r'transactions', TransactionViewSet, basename='transaction')

# Registra o PublicTransactionViewSet na rota 'public-transactions'.
router.register(r'public-transactions', PublicTransactionViewSet, basename='public-transaction')

# As urlpatterns do app são as URLs geradas pelo router.
urlpatterns = router.urls
