import sys
import datetime
import json
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from radio.models import *

class Command(BaseCommand):
    help = 'Insert radio transmisison info'

    def add_arguments(self, parser):
        parser.add_argument('json_name')
        parser.add_argument(
            '--vhf',
            action='store_true',
            dest='vhf',
            default=False,
            help='Add a VHF tranmission',
        )

    def handle(self, *args, **options):
        print('Just a test')
        vhf = options['vhf']
        json_f = options['json_name']
        print('You passed in {}'.format(json_f))
        add_new_trans(json_f, vhf)



def add_new_trans(file_name,vhf):

    if vhf:
        tg_dec = file_name.split('_', 1)[0]
        # 90002_cnf_20160903_015052.mp3
        file_dt = file_name.split('_')[2]
        file_time = file_name.split('_')[3].split('.')[0]
        full_dt = "{}{}".format(file_dt,file_time)
        epoc_ts = datetime.datetime.strptime(full_dt, "%Y%m%d%H%M%S").timestamp()
        # XXX - ARGGGGGGGGGGGGG FIX THIS ASAP, convert to the time
        epoc_ts = epoc_ts - 25200
        #pytz.timezone('UTC').localize(new_time, is_dst=None)
        #epoc_ts = new_time.timestamp()
        print("Time {} is {}".format(full_dt,epoc_ts))
        #epoc_ts.replace(tzinfo=pytz.UTC)
    else:
        tg_dec = file_name.split('-', 1)[0]
        epoc_ts = file_name.split('-', 2)[1].split('_', 1)[0]
    print("TalkGroup", tg_dec)
    if vhf:
        freq = 0
    else:
        freq = file_name.split('_', 2)[1]
    try:
        tg = TalkGroup.objects.get(dec_id=tg_dec)
    except TalkGroup.DoesNotExist:
        tg = TalkGroup.objects.create(dec_id=tg_dec, alpha_tag='UNK')

    dt = datetime.datetime.fromtimestamp(int(epoc_ts))
    #if vhf:
    #  dt.replace(tzinfo=pytz.UTC)
    t = Transmission( start_datetime = dt,
                     audio_file = file_name,
                     talkgroup = tg_dec,
                     talkgroup_info = tg,
                     freq = int(float(freq)),
                     emergency = False,
                   )
    if not vhf:
        with open('audio_files/{}.json'.format(file_name)) as data_file:    
            data = json.load(data_file)
        if data:
            if data['emergency']:
                t.emergency = True
            count = 0
            t.play_length = data['play_length']
            t.save()
            for trans_unit in data['srcList']:
                u,created = Unit.objects.get_or_create(dec_id=trans_unit)
                tu = TranmissionUnit.objects.create(transmission=t, unit=u, order=count)
                count=count+1
    else:
        t.save()
