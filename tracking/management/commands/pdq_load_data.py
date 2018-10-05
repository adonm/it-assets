from django.core.management.base import BaseCommand
from tracking.utils_pdq import pdq_load_computers


class Command(BaseCommand):
    help = 'Loads data from PDQ Inventory scans.'

    def handle(self, *args, **options):
        pdq_load_computers()
