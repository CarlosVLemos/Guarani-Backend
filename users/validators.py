import os
from django.core.exceptions import ValidationError
from rest_framework import serializers

def validate_file_type_and_size(file):

    # 1. Validação do Tamanho do Arquivo (5 MB)
    max_file_size = 5 * 1024 * 1024
    if file.size > max_file_size:
        raise serializers.ValidationError(f"O arquivo é muito grande ({file.size / 1024 / 1024:.2f} MB). O tamanho máximo permitido é de {max_file_size / 1024 / 1024:.0f} MB.")

    # 2. Validação da Extensão do Arquivo
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise serializers.ValidationError(f"Tipo de arquivo ('{ext}') não suportado. Use um dos seguintes: {', '.join(allowed_extensions)}")
