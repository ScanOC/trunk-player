import sys
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from radio.models import *
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Import units list from csv file'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument('--update', action='store_true', help='Update the units if they already exist')
    def handle(self, *args, **options):
        f_name = options['file']
        update = options['update']
        import_unit_file(f_name, update=update)

def import_unit_file(file_name, update=False):
    line = 0
    with open(file_name) as f:
        line += 1
        units = csv.reader(f, delimiter=',', quotechar='"')
        for row in units:
            try:
                agency = Agency.objects.get(id=row[2])
            except Agency.DoesNotExist:
                print("Error, Agency in line {} does not exist, skipping".format(line))
                continue
            try:
                system = System.objects.get(id=row[5])
            except System.DoesNotExist:
                print("Error, System in line {} does not exist, skipping".format(line))
                continue
            try:
                unit, created = Unit.objects.get_or_create(dec_id=row[0], defaults={'description': row[1], 'agency': agency, 'type': row[3], 'number': row[4], 'system': system, 'slug': row[6]})
                if not created and update:
                    # Update the unit if it already exists and update flag is set
                    unit.description = row[1]
                    unit.agency = agency
                    unit.type = row[3]
                    unit.number = row[4]
                    unit.system = system
                    unit.slug = row[6]
                    unit.save()
            except (IntegrityError, IndexError):
                print("Already In DB Skipping {} line {}".format(row[1], line))
