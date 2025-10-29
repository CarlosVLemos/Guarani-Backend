from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    BaseUserViewSet,
    OfertanteProfileViewSet,
    OfertanteDocumentViewSet,
    CompradorProfileViewSet,
    CompradorOrganizationViewSet,
    CompradorRequirementsViewSet,
    CompradorDocumentsViewSet,
    # Views para Auth com tags do Swagger
    TokenObtainPairView,
    TokenRefreshView,
)

# Cria um router para registrar os ViewSets
router = DefaultRouter()
router.register(r'', BaseUserViewSet, basename='user')
router.register(r'ofertante-profiles', OfertanteProfileViewSet, basename='ofertante-profile')
router.register(r'ofertante-documents', OfertanteDocumentViewSet, basename='ofertante-document')
router.register(r'comprador-profiles', CompradorProfileViewSet, basename='comprador-profile')
router.register(r'comprador-organizations', CompradorOrganizationViewSet, basename='comprador-organization')
router.register(r'comprador-requirements', CompradorRequirementsViewSet, basename='comprador-requirement')
router.register(r'comprador-documents', CompradorDocumentsViewSet, basename='comprador-document')


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Inclui as rotas geradas pelo router
    path('', include(router.urls)),
]
