
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    """
    View para registrar um novo usuário (Ofertante).
    Acessível por qualquer um (AllowAny).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] # Permite que qualquer um acesse esta view
