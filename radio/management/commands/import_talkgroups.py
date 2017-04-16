import sys
import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Import talkgroup info'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument(
            '--system',
            type=int,
            help='Export talkgroups from only this system',
            required=True,
        )

    def handle(self, *args, **options):
        import_tg_file(self, options)


def import_tg_file(self, options):
    ''' Using the talkgroup file from trunk-recorder'''
    file_name = options['file']
    system_id = options['system']
    try:
        system = System.objects.get(pk=system_id)
    except System.DoesNotExist:
        self.stdout.write("Valid systems")
        for system in System.objects.all():
            self.stdout.write("#{} - {}".format(system.pk, system.name))
        raise CommandError('System #{} was not a valid system'.format(system_id))
    self.stdout.write("Importing talkgroups for system #{} - {}".format(system.pk, system.name))
    with open(file_name) as tg_file:
        tg_info = csv.reader(tg_file, delimiter=',', quotechar='"')
        for row in tg_info:
            try:
                obj, create = TalkGroup.objects.update_or_create(dec_id=row[0], system=system, defaults={'mode': row[2], 'alpha_tag': row[3], 'description': row[4], 'priority': row[5]})
            except (IntegrityError, IndexError):
                print("Skipping {}".format(row[3]))

