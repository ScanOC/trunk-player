import sys
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from radio.models import *
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Import agency list from csv file'

    def add_arguments(self, parser):
        parser.add_argument('file')

    def handle(self, *args, **options):
        f_name = options['file']
        import_agency_file(f_name)


def import_agency_file(file_name):
    with open(file_name) as f:
        agency = csv.DictReader(f, skipinitialspace=True)
        for row in agency:
            try:
                Agency(name=row['name'], short=row['short']).save()
            except (IntegrityError, IndexError):
                print("Already In DB {} Skipping {}".format(row['short'],row['name']))

