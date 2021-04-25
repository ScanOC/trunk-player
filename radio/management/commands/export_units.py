import sys
import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *

class Command(BaseCommand):
    help = 'Export talkgroup info'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument(
            '-s',
            '--system',
            type=int,
            default=-1,
            help='Export units from only this system',
        )


    def handle(self, *args, **options):
        export_unit_file(self, options)


def export_unit_file(self, options):
    ''' Using the talkgroup file from trunk-recorder'''
    file_name = options['file']
    system = options['system']
    unit = Unit.objects.all()
    if system >= 0:
        unit = unit.filter(system=system)
        self.stdout.write("Exporting units for system #{}".format(system))
    else:
        self.stdout.write("Exporting units for all systems")
    with open(file_name, "w") as unit_file:
        for u in unit:
            dec_id = u.dec_id
            description = u.description
            agency = u.agency.pk
            type_ = u.type
            number = u.number
            system = u.system.pk
            slug = u.slug
            
            csv_fh = csv.writer(unit_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_fh.writerow([dec_id, description, agency, type_, number, system, slug])