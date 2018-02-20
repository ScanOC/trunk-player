import sys
import datetime
import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *

class Command(BaseCommand):
    help = 'Utility to update the talkgroup last_trasmission'

    def handle(self, *args, **options):
        update_tg(self, options)

def update_tg(self, options):
    talkgroups = TalkGroup.objects.all()
    set_count = 0
    for tg in talkgroups:
        transmission = Transmission.objects.filter(talkgroup_info=tg).first()
        if transmission:
            tg.last_transmission = transmission.start_datetime
            tg.save()
            set_count+=1
    self.stdout.write(self.style.SUCCESS('{} Talkgroups Updated'.format(set_count)))
