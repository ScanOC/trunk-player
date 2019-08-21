import os
import sys
from datetime import datetime
from datetime import timedelta
import json
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from radio.models import *
from django.db import transaction,connections,connection

db_name = connection.settings_dict['NAME']
db_engine = connection.vendor
print('db_name is "%s"' % db_name)
print('db_engine is "%s"' % db_engine)

class Command(BaseCommand):
    help = 'Prune transmisison table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            #action='store_true',
            #dest='source',
            default=5,
            help='Set the number of days older than to prune',
        )

    def handle(self, *args, **options):
        print('You passed in {}'.format(options['days']))
        purge_trans(options)



def purge_trans(options):

    days_opt = options['days']
    days_default = False
    if days_opt == -1:
        days_opt = 0
        days_default = True

    t = Transmission.objects.filter(start_datetime__lt=timezone.now() - timedelta(days=days_opt))
    print('Pruning %s transmissions older than %s days.' % (t.count(), days_opt))
    t.delete()
    print('Pruning complete')
    if 'sqlite' in db_engine:
        def vacuum_db(using='default'):
            cursor = connections[using].cursor()
            cursor.execute("VACUUM")
            transaction.commit()

        print ("Vacuuming database...")
        before = os.stat(db_name).st_size
        print ("Size before: %s bytes" % before)
        vacuum_db()
        after = os.stat(db_name).st_size
        print ("Size after: %s bytes" % after)
        print ("Reclaimed: %s bytes" % (before - after))
