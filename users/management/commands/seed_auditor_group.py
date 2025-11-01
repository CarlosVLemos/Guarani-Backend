from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Cria o grupo 'auditor' caso não exista."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="auditor")
        if created:
            self.stdout.write(self.style.SUCCESS("Grupo 'auditor' criado com sucesso."))
        else:
            self.stdout.write(self.style.WARNING("Grupo 'auditor' já existe."))
