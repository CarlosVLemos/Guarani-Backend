from django.core.management.base import BaseCommand
from calculator.services import train_and_save_model

class Command(BaseCommand):
    help = 'Treina o modelo de previsão de preços de CBIO'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando treinamento do modelo...')
        result = train_and_save_model()
        self.stdout.write(self.style.SUCCESS(f'Treinamento concluído: {result}'))