from django.core.management.base import BaseCommand, CommandError
from organisation.alesco.calmp_ict_view_v2 import alesco_db_import


class Command(BaseCommand):
    help = 'Synchronises user data from Alesco into the matching DepartmentUser objects'

    def add_arguments(self, parser):
        parser.add_argument('--update', action='store_true', help='Also update DepartmentUser field values')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Querying Alesco database for employee information'))
        try:
            alesco_db_import(update_dept_user=options['update'])
        except Exception as ex:
            self.stdout.write(self.style.ERROR(ex))
            raise CommandError('Syncronisation from Alesco database failed')
