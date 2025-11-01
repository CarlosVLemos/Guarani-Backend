
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from projects.models import Project
from marketplace.models import Transaction
from users.models import BaseUser

class Command(BaseCommand):
    """
    Comando Django para semear o banco de dados com transações de teste.

    Este seeder cria um histórico de transações de compra para cada usuário Comprador.

    Como usar:
    - Para adicionar novas transações: `python manage.py seed_transactions`
    - Para limpar transações antigas e depois adicionar novas: `python manage.py seed_transactions --clear`
    """
    help = "Semeia o banco de dados com transações de teste, criando um histórico para cada comprador."

    def add_arguments(self, parser):
        # Adiciona o argumento --clear, que quando presente, armazena True
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Limpa a tabela de transações antes de inserir novos dados.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando o seeder de transações..."))

        # Se a flag --clear for usada, limpa as transações existentes
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Opção --clear ativada. Limpando todas as transações existentes..."))
            count, _ = Transaction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"{count} transações foram deletadas."))

        # Buscar projetos e usuários necessários
        projects_available = list(Project.objects.alive().filter(price_per_credit__gt=0, carbon_credits_available__gt=0))
        compradores = BaseUser.objects.filter(user_type=BaseUser.UserType.COMPRADOR)

        if not projects_available:
            self.stdout.write(self.style.WARNING("Nenhum projeto com preço e créditos disponíveis encontrado. O seeder não pode continuar."))
            return

        if not compradores.exists():
            self.stdout.write(self.style.WARNING("Nenhum usuário 'Comprador' encontrado. O seeder não pode continuar."))
            return

        self.stdout.write(f"Encontrados {len(projects_available)} projetos disponíveis e {compradores.count()} compradores.")
        
        created_count = 0
        
        # Iterar sobre cada comprador para criar um histórico de transações
        for buyer in compradores:
            self.stdout.write(f"--- Criando transações para o comprador: {buyer.email} ---")
            
            # Filtrar projetos que não pertencem ao comprador
            projects_to_buy_from = [p for p in projects_available if p.ofertante != buyer]
            if not projects_to_buy_from:
                self.stdout.write(self.style.NOTICE(f"  - Nenhum projeto disponível para compra para {buyer.email}."))
                continue

            # Criar de 2 a 3 transações para este comprador
            num_transactions = random.randint(2, 3)
            for i in range(num_transactions):
                project = random.choice(projects_to_buy_from)

                # Definir quantidade e status da transação
                quantity = random.randint(1, min(project.carbon_credits_available, 25))
                total_price = Decimal(quantity) * project.price_per_credit
                transaction_status = random.choice(Transaction.Status.choices)[0]

                try:
                    Transaction.objects.create(
                        buyer=buyer,
                        project=project,
                        quantity=quantity,
                        price_per_credit_at_purchase=project.price_per_credit,
                        total_price=total_price,
                        status=transaction_status,
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"  - Transação {i+1} criada: Compra de {quantity} créditos do projeto '{project.name}' (Status: {transaction_status})"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"  - Erro ao criar transação para o comprador '{buyer.email}': {e}"
                    ))

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"\nTotal de {created_count} novas transações criadas com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING("\nNenhuma nova transação foi criada."))

