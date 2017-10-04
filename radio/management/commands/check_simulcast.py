import sys
import datetime
import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *

class Command(BaseCommand):
    help = 'Utility to make sure simulcast talkgroups are being recored'

    def add_arguments(self, parser):
        parser.add_argument('talkgroup1')
        parser.add_argument('talkgroup2')
        parser.add_argument(
            '-m',
            '--minutes',
            type=int,
            default=15,
            help='Minutes between transmissions before alerting'
        )

    def handle(self, *args, **options):
        check_tg(self, options)

def check_tg(self, options):
    tg_name1 = options['talkgroup1']
    tg_name2 = options['talkgroup2']
    try:
        tg1 = TalkGroup.objects.get(slug=tg_name1)
    except TalkGroup.DoesNotExist:
        self.stdout.write(self.style.ERROR('Talk Group {} does not exist, make sure you are using the slug name'.format(tg_name1)))
        sys.exit(2)
    try:
        tg2 = TalkGroup.objects.get(slug=tg_name2)
    except TalkGroup.DoesNotExist:
        self.stdout.write(self.style.ERROR('Talk Group {} does not exist, make sure you are using the slug name'.format(tg_name2)))
        sys.exit(3)

    last_tg1 = Transmission.objects.filter(talkgroup_info=tg1)[0]
    last_tg2 = Transmission.objects.filter(talkgroup_info=tg2)[0]
    local_tz = pytz.timezone(settings.TIME_ZONE)
    settings_time_zone = local_tz
    time1 = last_tg1.start_datetime.astimezone(local_tz)
    time2 = last_tg2.start_datetime.astimezone(local_tz)
    if time1 >= time2:
        time_diff = time1 - time2
    else:
        time_diff = time2 - time1
    max_diff = timezone.timedelta(minutes=options['minutes'])
    
    self.stdout.write('Comparing Last Transmission {} {} to {} {} ({})'.format(tg1, time1, tg2, time2, time_diff))
    if time_diff > max_diff:
        self.stdout.write(self.style.ERROR('Too long between simulcast transmissions {}'.format(time_diff)))
        sys.exit(1)
    else:
        self.stdout.write(self.style.SUCCESS('Good'))
