import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import (
    BaseUser, OfertanteProfile, CompradorProfile, CompradorOrganization,
    CompradorRequirements, CompradorDocuments
)
from projects.models import Project, Document
from marketplace.models import Transaction

# Senha padrão para todos os usuários criados
DEFAULT_PASSWORD = "Teste#123"

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste para ofertantes, compradores, projetos e transações.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Limpa os dados existentes antes de popular o banco.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando o processo de seeding com dados customizados..."))
        
        seeded_users_emails = []

        if options['clean']:
            self.stdout.write(self.style.WARNING("Limpando o banco de dados..."))
            Transaction.objects.all().delete()
            Document.objects.all().delete()
            Project.objects.all().delete()
            OfertanteProfile.objects.all().delete()
            CompradorProfile.objects.all().delete()
            CompradorOrganization.objects.all().delete()
            CompradorRequirements.objects.all().delete()
            CompradorDocuments.objects.all().delete()
            BaseUser.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Banco de dados limpo."))

        self.stdout.write("Criando usuários e perfis...")

        # --- Criação de Ofertantes Específicos ---
        ofertante_alvaro_email = "ofertante.alvaro@example.com"
        ofertante_alvaro, created = BaseUser.objects.get_or_create(
            email=ofertante_alvaro_email,
            defaults={'user_type': BaseUser.UserType.OFERTANTE, 'is_verified': True, 'verification_status': BaseUser.VerificationStatus.APPROVED}
        )
        if created: ofertante_alvaro.set_password(DEFAULT_PASSWORD); ofertante_alvaro.save()
        OfertanteProfile.objects.update_or_create(user=ofertante_alvaro, defaults={'organization_name': "Sítio do Alvaro Amarelo", 'contact_name': "Alvaro"})
        seeded_users_emails.append(ofertante_alvaro_email)

        ofertante_samara_email = "ofertante.samara@example.com"
        ofertante_samara, created = BaseUser.objects.get_or_create(
            email=ofertante_samara_email,
            defaults={'user_type': BaseUser.UserType.OFERTANTE, 'is_verified': True, 'verification_status': BaseUser.VerificationStatus.APPROVED}
        )
        if created: ofertante_samara.set_password(DEFAULT_PASSWORD); ofertante_samara.save()
        OfertanteProfile.objects.update_or_create(user=ofertante_samara, defaults={'organization_name': "Samara Renova Guamá", 'contact_name': "Samara"})
        seeded_users_emails.append(ofertante_samara_email)

        ofertante_kettlyn_email = "ofertante.kettlyn@example.com"
        ofertante_kettlyn, created = BaseUser.objects.get_or_create(
            email=ofertante_kettlyn_email,
            defaults={'user_type': BaseUser.UserType.OFERTANTE, 'is_verified': True, 'verification_status': BaseUser.VerificationStatus.APPROVED}
        )
        if created: ofertante_kettlyn.set_password(DEFAULT_PASSWORD); ofertante_kettlyn.save()
        OfertanteProfile.objects.update_or_create(user=ofertante_kettlyn, defaults={'organization_name': "Kettlyn Transforma Belém", 'contact_name': "Kettlyn"})
        seeded_users_emails.append(ofertante_kettlyn_email)

        # --- Criação de Ofertante com Múltiplos Projetos ---
        ofertante_multi_email = "ofertante.grandesprojetos@example.com"
        ofertante_multi, created = BaseUser.objects.get_or_create(
            email=ofertante_multi_email,
            defaults={'user_type': BaseUser.UserType.OFERTANTE, 'is_verified': True, 'verification_status': BaseUser.VerificationStatus.APPROVED}
        )
        if created: ofertante_multi.set_password(DEFAULT_PASSWORD); ofertante_multi.save()
        OfertanteProfile.objects.update_or_create(user=ofertante_multi, defaults={'organization_name': "Grandes Projetos Sustentáveis", 'contact_name': "Felipe"})
        seeded_users_emails.append(ofertante_multi_email)

        # --- Criação de Comprador Específico ---
        comprador_rodrigo_email = "comprador.rodrigo@example.com"
        comprador_rodrigo, created = BaseUser.objects.get_or_create(
            email=comprador_rodrigo_email,
            defaults={'user_type': BaseUser.UserType.COMPRADOR, 'is_verified': True, 'verification_status': BaseUser.VerificationStatus.APPROVED, 'wallet_balance': Decimal("750000.00")}
        )
        if created: comprador_rodrigo.set_password(DEFAULT_PASSWORD); comprador_rodrigo.save()
        CompradorOrganization.objects.update_or_create(user=comprador_rodrigo, defaults={'company_name': "Rodrigo Concreta Belém", 'cnpj': "45.997.418/0001-53"})
        seeded_users_emails.append(comprador_rodrigo_email)

        self.stdout.write(self.style.SUCCESS(f"{len(seeded_users_emails)} usuários criados ou atualizados."))

        self.stdout.write("Criando projetos...")
        # Projetos Iniciais
        proj_alvaro = Project.objects.create(ofertante=ofertante_alvaro, name="sitio do alvaro amarelo", project_type=Project.ProjectType.AGRICULTURA, status=Project.Status.ACTIVE, carbon_credits_available=1000, price_per_credit=Decimal("50.00"))
        Project.objects.create(ofertante=ofertante_samara, name="Samara renova guama", project_type=Project.ProjectType.REFLORESTAMENTO, status=Project.Status.ACTIVE, carbon_credits_available=2500, price_per_credit=Decimal("75.00"))
        Project.objects.create(ofertante=ofertante_kettlyn, name="kettlyn transforma belem", project_type=Project.ProjectType.GESTAO_RESIDUOS, status=Project.Status.ACTIVE, carbon_credits_available=5000, price_per_credit=Decimal("60.00"))
        
        # Projetos do Ofertante Multi
        for i in range(1, 7):
            Project.objects.create(
                ofertante=ofertante_multi,
                name=f"Projeto Sustentável {i} - {ofertante_multi.ofertante_profile.organization_name}",
                project_type=random.choice(Project.ProjectType.choices)[0],
                status=random.choice([Project.Status.ACTIVE, Project.Status.VALIDATED]),
                carbon_credits_available=random.randint(1000, 20000),
                price_per_credit=Decimal(random.uniform(40.0, 150.0))
            )
        self.stdout.write(self.style.SUCCESS("9 projetos criados."))

        self.stdout.write("Criando transação de exemplo...")
        if not Transaction.objects.filter(buyer=comprador_rodrigo, project=proj_alvaro).exists():
            Transaction.objects.create(buyer=comprador_rodrigo, project=proj_alvaro, quantity=50, price_per_credit_at_purchase=proj_alvaro.price_per_credit, total_price=proj_alvaro.price_per_credit * 50)
            self.stdout.write(self.style.SUCCESS("1 transação criada."))

        # Escreve os emails dos usuários criados em um arquivo
        try:
            with open("seeded_users.txt", "w") as f:
                f.write("Usuários criados pelo seeder:\n")
                f.write("Senha padrão para todos: " + DEFAULT_PASSWORD + "\n\n")
                for email in seeded_users_emails:
                    f.write(email + "\n")
            self.stdout.write(self.style.SUCCESS("Arquivo 'seeded_users.txt' criado com sucesso."))
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Não foi possível escrever o arquivo 'seeded_users.txt': {e}"))

        self.stdout.write(self.style.SUCCESS("Seeding customizado concluído com sucesso!"))
