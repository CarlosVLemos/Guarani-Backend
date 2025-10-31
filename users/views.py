from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from .serializers import (
    BaseUserSerializer,
    CompradorProfileSerializer, CompradorOrganizationSerializer,
    CompradorRequirementsSerializer, CompradorDocumentsSerializer,
    OfertanteProfileSerializer, OfertanteDocumentSerializer,
    UserRegistrationSerializer,
    UserMeSerializer,
)
from .models import (
    CompradorProfile, CompradorOrganization,
    CompradorRequirements, CompradorDocuments,
    OfertanteProfile, OfertanteDocument
)
from .permissions import IsOwnerOrAdmin

User = get_user_model()

@extend_schema(tags=['Auth'])
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['users'])
class BaseUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = BaseUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        # Admin vê todos, usuários normais só se veem.
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(pk=user.pk)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Retorna informações do usuário atual, incluindo grupos e is_auditor."""
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def verify(self, request, pk=None):
        user = self.get_object()
        status_ = request.data.get("verification_status")
        if status_ not in [s.value for s in User.VerificationStatus]:
            return Response({"detail": "Status de verificação inválido."}, status=status.HTTP_400_BAD_REQUEST)
        user.verification_status = status_
        user.is_verified = (status_ == User.VerificationStatus.APPROVED)
        user.save()
        
        ser = self.get_serializer(user)
        return Response(ser.data)

# --- ViewSets para Ofertante ---

@extend_schema(tags=['Ofertante'])
class OfertanteProfileViewSet(viewsets.ModelViewSet):
    queryset = OfertanteProfile.objects.all()
    serializer_class = OfertanteProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

@extend_schema(tags=['Ofertante'])
class OfertanteDocumentViewSet(viewsets.ModelViewSet):
    queryset = OfertanteDocument.objects.all()
    serializer_class = OfertanteDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

# --- ViewSets para Comprador ---

@extend_schema(tags=['Comprador'])
class CompradorProfileViewSet(viewsets.ModelViewSet):
    queryset = CompradorProfile.objects.all()
    serializer_class = CompradorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

@extend_schema(tags=['Comprador'])
class CompradorOrganizationViewSet(viewsets.ModelViewSet):
    queryset = CompradorOrganization.objects.all()
    serializer_class = CompradorOrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

@extend_schema(tags=['Comprador'])
class CompradorRequirementsViewSet(viewsets.ModelViewSet):
    queryset = CompradorRequirements.objects.all()
    serializer_class = CompradorRequirementsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

@extend_schema(tags=['Comprador'])
class CompradorDocumentsViewSet(viewsets.ModelViewSet):
    queryset = CompradorDocuments.objects.all()
    serializer_class = CompradorDocumentsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)
    
@extend_schema(tags=['Auth'])
class TokenObtainPairView(BaseTokenObtainPairView):

    pass

@extend_schema(tags=['Auth'])
class TokenRefreshView(BaseTokenRefreshView):
    pass