# API - Olho no Verde

Esta é a aplicação backend para o projeto Olho no Verde. A API é construída com Django e Django Rest Framework, e é totalmente containerizada usando Docker para facilitar o desenvolvimento e a implantação.

## Pré-requisitos

Antes de começar, garanta que você tenha as seguintes ferramentas instaladas na sua máquina:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Como Rodar o Projeto

Siga os passos abaixo para configurar e executar o ambiente de desenvolvimento local.

### 1. Clone o Repositório

Se você ainda não o fez, clone o projeto para a sua máquina local.

```bash
git clone  https://github.com/CarlosVLemosolho-no-verde-backend
```

### 2. Configure as Variáveis de Ambiente

O projeto utiliza um arquivo `.env` para gerenciar as configurações sensíveis, como chaves de API e credenciais de banco de dados. Você pode começar copiando o arquivo de exemplo:

```bash
cp .env.example .env
```

O arquivo `.env.example` já contém os valores padrão para o ambiente de desenvolvimento com Docker. Você não precisa alterar nada para começar, mas sinta-se à vontade para revisar os valores.

### 3. Suba os Contêineres

Com o Docker e o Docker Compose instalados, use o seguinte comando na raiz da pasta `app/` para construir as imagens e iniciar os contêineres da API, do banco de dados (Postgres) e do Redis:

```bash
docker-compose up --build
```

O argumento `--build` garante que a imagem da sua API será reconstruída se você tiver feito alterações (como adicionar novas dependências). Na primeira vez que você rodar, o Docker fará o download das imagens do Postgres e do Redis, o que pode levar alguns minutos.

### 4. Execute as Migrações do Banco de Dados

Com os contêineres em execução, abra um **novo terminal** e execute as migrações do Django para criar as tabelas no banco de dados. O comando `docker-compose exec` permite executar comandos dentro de um contêiner que já está rodando.

```bash
docker-compose exec api python manage.py migrate
```

### 5. Crie um Superusuário (Opcional)

Se você quiser acessar a área de administração do Django, crie um superusuário:

```bash
docker-compose exec api python manage.py createsuperuser
```

Siga as instruções no terminal para definir o nome de usuário, email e senha.

## Acessando a Aplicação

Pronto! Sua aplicação está no ar e acessível nos seguintes endereços:

- **API Principal**: [http://localhost:8000/](http://localhost:8000/)
- **Documentação da API (Swagger UI)**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **Admin do Django**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
