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
        parser.add_argument(
            '--update',
            dest='update',
            action='store_true',
            help='Update existing records',
            default=False,
       )

    def handle(self, *args, **options):
        import_unit_file(options)


def import_unit_file(options):
    line = 0
    file_name = options['file']
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
            try_update = True
            try:
                Unit(dec_id=row[0], description=row[1], agency=agency, type=row[3], number=row[4], system=system, slug=row[6]).save()
                try_update = False
            except IntegrityError:
                if not options['update']:
                    print("Already In DB Skipping {} line {}".format(row[1], line))
            except IndexError:
                print('Error with data in line {}'.format(line))

            if try_update and options['update']:
                try:
                    existing_unit = Unit.objects.get(dec_id=row[0], system=system)
                except Unit.DoesNotExist:
                     print('Error with data in line {}'.format(line))
                try:
                    existing_unit.description=row[1]
                    existing_unit.agency=agency
                    existing_unit.type=row[3]
                    existing_unit.number=row[4]
                    existing_unit.slug=row[6]
                except IndexError:
                    print('Error with data in line {}'.format(line))
                existing_unit.save()

