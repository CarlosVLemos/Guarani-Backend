import random
from decimal import Decimal
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import Project, Document
from marketplace.models import Transaction
from users.models import OfertanteProfile, CompradorProfile, CompradorOrganization

User = get_user_model()

# --- Dados para os Projetos Fictícios (Inspirado no Pará) ---
PROJECT_DATA = [
    {
        "name": "Guardiões de Paragominas",
        "description": "Protege 50.000 hectares de floresta primária em Paragominas, evitando o desmatamento e apoiando comunidades locais com monitoramento participativo.",
        "project_type": Project.ProjectType.REFLORESTAMENTO,
        "location": "Paragominas, Pará",
        "status": Project.Status.ACTIVE,
        "credits": 150000,
        "price": Decimal("85.50")
    },
    {
        "name": "Renova Xingu",
        "description": "Recuperação de 10.000 hectares de pastagens degradadas em Altamira com espécies nativas da Amazônia, criando um corredor ecológico.",
        "project_type": Project.ProjectType.REFLORESTAMENTO,
        "location": "Altamira, Pará",
        "status": Project.Status.ACTIVE,
        "credits": 85000,
        "price": Decimal("92.00")
    },
    {
        "name": "Agrofloresta Tomé-Açu",
        "description": "Produção sustentável de cacau e açaí em sistema agroflorestal, combinando geração de renda para agricultores familiares com a captura de carbono.",
        "project_type": Project.ProjectType.AGRICULTURA,
        "location": "Tomé-Açu, Pará",
        "status": Project.Status.ACTIVE,
        "credits": 40000,
        "price": Decimal("110.00")
    },
    {
        "name": "Energia Limpa de Tucuruí",
        "description": "Projeto de substituição de geradores a diesel por painéis solares em comunidades ribeirinhas próximas a Tucuruí.",
        "project_type": Project.ProjectType.ENERGIA_RENOVAVEL,
        "location": "Tucuruí, Pará",
        "status": Project.Status.VALIDATED,
        "credits": 60000,
        "price": Decimal("78.00")
    }
]

class Command(BaseCommand):
    help = "Popula o banco de dados com dados de teste para usuários, projetos e transações."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa os dados existentes (exceto superusuários) antes de popular.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Limpando o banco de dados...'))
            Transaction.objects.all().delete()
            Document.objects.all().delete()
            Project.objects.all().delete()
            OfertanteProfile.objects.all().delete()
            CompradorProfile.objects.all().delete()
            CompradorOrganization.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Banco de dados limpo.'))

        self.stdout.write('Iniciando a população do banco de dados...')

        # --- 1. Criação de Usuários e Perfis ---
        self.stdout.write('Criando usuários e perfis...')
        
        ofertante1, _ = User.objects.get_or_create(
            email='biofloresta@example.com',
            defaults={'user_type': User.UserType.OFERTANTE, 'is_verified': True}
        )
        ofertante1.set_password('senha123')
        ofertante1.save()
        OfertanteProfile.objects.get_or_create(
            user=ofertante1,
            defaults={
                'organization_name': 'BioFloresta Sustentável',
                'contact_name': 'Juliana Costa',
                'phone': '91988887777',
                'organization_type': OfertanteProfile.OrganizationType.ONG
            }
        )

        ofertante2, _ = User.objects.get_or_create(
            email='carbonzero@example.com',
            defaults={'user_type': User.UserType.OFERTANTE, 'is_verified': True}
        )
        ofertante2.set_password('senha123')
        ofertante2.save()
        OfertanteProfile.objects.get_or_create(
            user=ofertante2,
            defaults={
                'organization_name': 'Carbon Zero Soluções',
                'contact_name': 'Marcos Silva',
                'phone': '91955554444',
                'organization_type': OfertanteProfile.OrganizationType.EMPRESA_PRIVADA
            }
        )

        comprador1, _ = User.objects.get_or_create(
            email='mineradora.norte@example.com',
            defaults={'user_type': User.UserType.COMPRADOR, 'is_verified': True}
        )
        comprador1.set_password('senha123')
        comprador1.save()
        CompradorOrganization.objects.get_or_create(
            user=comprador1,
            defaults={'company_name': 'Mineradora Norte S.A.', 'cnpj': '11.222.333/0001-44', 'website': 'https://example.com'}
        )

        comprador2, _ = User.objects.get_or_create(
            email='varejista.brasil@example.com',
            defaults={'user_type': User.UserType.COMPRADOR, 'is_verified': True}
        )
        comprador2.set_password('senha123')
        comprador2.save()
        CompradorOrganization.objects.get_or_create(
            user=comprador2,
            defaults={'company_name': 'Varejista Brasil Ltda', 'cnpj': '44.555.666/0001-77', 'website': 'https://example.com'}
        )

        self.stdout.write(self.style.SUCCESS('Usuários e perfis criados.'))

        # --- 2. Criação de Projetos ---
        self.stdout.write('Criando projetos...')
        ofertantes = [ofertante1, ofertante2]
        for data in PROJECT_DATA:
            project, created = Project.objects.get_or_create(
                name=data['name'],
                defaults={
                    'ofertante': random.choice(ofertantes),
                    'description': data['description'],
                    'project_type': data['project_type'],
                    'location': data['location'],
                    'status': data['status'],
                    'carbon_credits_available': data['credits'],
                    'price_per_credit': data['price']
                }
            )
            if created:
                self.stdout.write(f'  -> Projeto "{project.name}" criado.')
        self.stdout.write(self.style.SUCCESS('Projetos criados.'))

        # --- 3. Simulação de Transações ---
        self.stdout.write('Simulando transações...')
        compradores = [comprador1, comprador2]
        projetos_verificados = Project.objects.filter(status=Project.Status.VALIDATED, carbon_credits_available__gt=0)

        if not projetos_verificados.exists():
            self.stdout.write(self.style.WARNING('Nenhum projeto verificado com créditos disponíveis para simular transações.'))
            return

        for i in range(10): # Criar 10 transações
            comprador = random.choice(compradores)
            projeto = random.choice(projetos_verificados)
            
            if projeto.carbon_credits_available < 10:
                continue # Pula se o projeto tem poucos créditos

            quantidade = random.randint(10, min(projeto.carbon_credits_available, 500))
            preco_total = quantidade * projeto.price_per_credit

            if comprador.wallet_balance < preco_total:
                self.stdout.write(self.style.WARNING(f'  -! Saldo insuficiente para {comprador.email} comprar do projeto {projeto.name}. Tentativa {i+1}/10'))
                continue

            # Transação Atômica para a compra
            with transaction.atomic():
                # Debita do comprador e credita ao vendedor
                comprador.wallet_balance -= preco_total
                projeto.ofertante.wallet_balance += preco_total
                comprador.save()
                projeto.ofertante.save()

                # Atualiza os créditos do projeto
                projeto.carbon_credits_available -= quantidade
                projeto.save()

                # Cria o registro da transação
                Transaction.objects.create(
                    buyer=comprador,
                    project=projeto,
                    quantity=quantidade,
                    price_per_credit_at_purchase=projeto.price_per_credit,
                    total_price=preco_total
                )
                self.stdout.write(f'  -> Transação {i+1}: {comprador.email} comprou {quantidade} créditos de "{projeto.name}".')

        self.stdout.write(self.style.SUCCESS('Transações simuladas.'))
        self.stdout.write(self.style.SUCCESS('\nBanco de dados populado com sucesso!'))
