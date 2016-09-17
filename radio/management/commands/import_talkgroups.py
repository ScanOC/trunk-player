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

    def handle(self, *args, **options):
        print('Just a test')
        f_name = options['file']
        print('You passed in {}'.format(f_name))
        import_tg_file(f_name)


def import_tg_file(file_name):
    ''' Uisng the talkgroup file from trunk-recorder'''
    with open(file_name) as tg_file:
        tg_info = csv.reader(tg_file, delimiter=',', quotechar='"')
        for row in tg_info:
            try:
                TalkGroup(dec_id=row[0], alpha_tag=row[3], description=row[4], common_name=row[6]).save()
            except (IntegrityError, IndexError):
                print("Skipping {}".format(row[3]))

