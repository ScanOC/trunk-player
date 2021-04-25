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

    def handle(self, *args, **options):
        f_name = options['file']
        import_unit_file(f_name)


def import_unit_file(file_name):
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
                Unit(dec_id=row[0], description=row[1], agency=agency, type=row[3], number=row[4], system=system, slug=row[6]).save()
            except (IntegrityError, IndexError):
                print("Already In DB Skipping {} line {}".format(row[1], line))
