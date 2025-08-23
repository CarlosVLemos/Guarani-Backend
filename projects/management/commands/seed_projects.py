
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from projects.models import Project, Document
from decimal import Decimal
import random


DATA = [
    dict(name="REDD+ Amazônia Tapajós", project_type="REDD", location="Pará, Brasil",
         lat=-4.255, lon=-55.983, credits=120000, price=Decimal("5.50"), status="ACTIVE"),
    dict(name="Eólica Ventos do Nordeste", project_type="Wind", location="Rio Grande do Norte, Brasil",
         lat=-5.793, lon=-35.198, credits=90000, price=Decimal("3.80"), status="VALIDATED"),
    dict(name="Solar Sertão Luz", project_type="Solar", location="Bahia, Brasil",
         lat=-12.970, lon=-38.512, credits=65000, price=Decimal("2.90"), status="ACTIVE"),
    dict(name="Biomassa Cerrado Vivo", project_type="Biomass", location="Goiás, Brasil",
         lat=-16.686, lon=-49.264, credits=40000, price=Decimal("4.20"), status="DRAFT"),
    dict(name="Reflorestamento Mata Atlântica", project_type="ARR", location="São Paulo, Brasil",
         lat=-23.550, lon=-46.633, credits=75000, price=Decimal("6.10"), status="ACTIVE"),
    dict(name="Hídrica Serra Azul", project_type="Hydro", location="Minas Gerais, Brasil",
         lat=-19.920, lon=-43.938, credits=50000, price=Decimal("3.10"), status="ACTIVE"),
    dict(name="Metano Aterro Verde", project_type="Methane Capture", location="Paraná, Brasil",
         lat=-25.428, lon=-49.273, credits=30000, price=Decimal("4.90"), status="VALIDATED"),
    dict(name="Cozinhas Limpas Ribeirinhas", project_type="Cookstoves", location="Amazonas, Brasil",
         lat=-3.132, lon=-60.023, credits=20000, price=Decimal("2.10"), status="ACTIVE"),
]


class Command(BaseCommand):
    help = "Cria usuários e 8 projetos com documentos mockados."

    def handle(self, *args, **options):
        User = get_user_model()
        seller1, _ = User.objects.get_or_create(username="ofertante1", defaults={"email": "of1@example.com"})
        seller2, _ = User.objects.get_or_create(username="ofertante2", defaults={"email": "of2@example.com"})
        buyer, _ = User.objects.get_or_create(username="comprador", defaults={"email": "buy@example.com"})

        owners = [seller1, seller2]
        created = 0

        for item in DATA:
            proj, created_now = Project.objects.get_or_create(
                name=item["name"],
                defaults=dict(
                    description=f"Projeto {item['project_type']} em {item['location']}.",
                    project_type=item["project_type"],
                    location=item["location"],
                    latitude=item["lat"],
                    longitude=item["lon"],
                    carbon_credits_available=item["credits"],
                    price_per_credit=item["price"],
                    status=item["status"],
                    owner=random.choice(owners),
                ),
            )
            if created_now:
                content = ContentFile(b"%PDF-1.4\n% Mock\n")
                doc = Document(project=proj, name="Ficha Técnica.pdf")
                doc.file.save("ficha_tecnica.pdf", content, save=True)
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed finalizado. Projetos criados: {created}"))
