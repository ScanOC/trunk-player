import sys
import datetime
import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *

class Command(BaseCommand):
    help = 'Utility to update the talkgroup recent_usage'

    def handle(self, *args, **options):
        update_tg(self, options)

def update_tg(self, options):
    recent_minutes = settings.TALKGROUP_RECENT_LENGTH
    compare_dt = timezone.now() - timezone.timedelta(minutes=15)
    talkgroups = TalkGroup.objects.filter(last_transmission__gte=compare_dt)
    set_count = 0
    unset_count = 0
    for tg in talkgroups:
        length = 0.0
        transmissions = Transmission.objects.filter(start_datetime__gte=compare_dt).filter(talkgroup_info=tg)
        for t in transmissions:
            length += t.play_length
        tg.recent_usage = int(length)
        tg.save()
        set_count+=1
    reset_tgs = TalkGroup.objects.filter(recent_usage__gt=0)
    for tg in reset_tgs:
        if tg in talkgroups:
            continue
        tg.recent_usage = 0
        tg.save()
        unset_count+=1
    self.stdout.write(self.style.SUCCESS('{} Talkgroups Updated, {} Talkgroups reset to 0'.format(set_count, unset_count)))
