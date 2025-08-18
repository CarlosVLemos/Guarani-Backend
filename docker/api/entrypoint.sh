#!/bin/sh

# Para o script se um comando falhar
set -e

# Define a porta do banco de dados se não estiver definida
DB_PORT=${DB_PORT:-5432}

# Aguarda o banco de dados ficar pronto
echo "Aguardando o banco de dados..."
while ! nc -z db $DB_PORT; do
  sleep 1
done
echo "Banco de dados pronto."

# Aplica as migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate
echo "Migrações aplicadas."

# Executa o comando passado para o script (o CMD do Dockerfile ou o command do docker-compose)
exec "$@"
