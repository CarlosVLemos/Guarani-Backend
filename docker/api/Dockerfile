FROM python:3.12-slim

# Evitar bytecode e buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório do projeto
WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar código do projeto
COPY . .

# Dar permissão de execução
RUN chmod +x /app/docker/api/entrypoint.sh

# Definir o entrypoint
ENTRYPOINT ["/app/docker/api/entrypoint.sh"]

# Rodar servidor de desenvolvimento
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]