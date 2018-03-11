import os
import sys
import datetime
import json
import pytz
from redis.exceptions import ConnectionError, RedisError
from radio.utility import RedisQueue


from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from radio.models import *


class Command(BaseCommand):
    help = 'Insert radio transmisison info'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exit-on-error',
            action='store_true',
            dest='exitonerror',
            default=False,
            help='Exit if there is an excepton'
        )

    def handle(self, *args, **options):
        q = RedisQueue('new_trans')
        running = True
        count = 0
        start_time = None
        while running:
            try:
                options['source'] = -1
                options['system'] = -1
                options['web_url'] = '/'
                options['verbose'] = False
                options['m4a'] = False
                options['vhf'] = False
                options['json_name'] = None
                
                if count == 0:
                   start_time = timezone.now()
                item = q.get()
                item_str = item.decode('utf-8')
                for part in item_str.split('|'):
                    rec = part.split(':')
                    try:
                        options[rec[0]] = rec[1]
                    except IndexError:
                        options[rec[0]] = True
                print('Adding json {}'.format(options['json_name']))
                add_new_trans(options)
                if count > 100:
                    end_time = timezone.now()
                    print('100 in {} to {}'.format(start_time, end_time ))
                    count = 0
                else:
                    count+=1
                

            except ConnectionError:
                print('Cannot connect to redis is it running?')
                running = False

            except KeyboardInterrupt:
                print('Exiting...')
                running = False

            except RedisError:
                print('Reconnecting...')
                q = RedisQueue('new_trans')

            except Exception as e:
                print('Error')
                print(e)
                if options['exitonerror']:
                    raise
                else:
                    pass

def talkgroup(tg_dec,system):
    try:
        tg = TalkGroup.objects.get(dec_id=tg_dec, system=system)
    except TalkGroup.DoesNotExist:
        name = '#{}'.format(tg_dec)
        tg = TalkGroup.objects.create(dec_id=tg_dec, system=system, alpha_tag=name, description='TalkGroup {}'.format(name))
    return tg

def add_new_trans(options):

    full_file_name = options['json_name']
    file_name = os.path.basename(full_file_name)
    vhf = options['vhf']
    source_opt = int(options['source'])
    system_opt = int(options['system'])
    web_url_opt = options['web_url']
    verbose = options['verbose']
    if verbose:
        print('You passed in {}'.format(options['json_name']))
    source_default = False
    if source_opt == -1:
        source_opt = 0
        source_default = True
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
        if verbose:
            print("Time {} is {}".format(full_dt,epoc_ts))
        #epoc_ts.replace(tzinfo=pytz.UTC)
    else:
        tg_dec = file_name.split('-', 1)[0]
        epoc_ts = file_name.split('-', 2)[1].split('_', 1)[0]
    if verbose:
        print("TalkGroup", tg_dec)
    if vhf:
        freq = 0
    else:
        freq = file_name.split('_', 2)[1]

    dt = datetime.datetime.fromtimestamp(int(epoc_ts), pytz.UTC)
    #if vhf:
    #dt.replace(tzinfo=pytz.UTC)
    try:
        source = Source.objects.get(pk=source_opt)
    except Source.DoesNotExist:
        source = Source.objects.create(pk=source_opt, description='Source #{}'.format(source_opt))

    t = Transmission( start_datetime = dt,
                     audio_file = file_name,
                     talkgroup = tg_dec,
                     freq = int(float(freq)),
                     emergency = False,
                     source = source,
                     audio_file_url_path = web_url_opt,
                   )
    system = 0
    if options['m4a']:
        t.audio_file_type = 'm4a'
    if not vhf:
        # First try and open file with given path, if not fail back
        # to old hardcoded audio_files path
        json_file = '{}.json'.format(full_file_name)
        if not os.path.exists(json_file):
            json_file = 'audio_files/{}.json'.format(file_name)
        try:
            with open(json_file) as data_file:
                data = json.load(data_file)
        except Exception as error: 
            return
        if data:
            if data['emergency']:
                t.emergency = True
            count = 0
            t.play_length = data.get('play_length',0)
            start_ts = data.get('start_time', 0)
            end_ts = data.get('stop_time', 0)
            if t.play_length == 0 and start_ts > 0 and end_ts > 0:
                t.play_length = end_ts - start_ts
            if end_ts:
                t.end_datetime = datetime.datetime.fromtimestamp(end_ts, pytz.UTC)
            system = data.get('system', 0)
            if system_opt >= 0: 
                system = system_opt # Command line overrides json
            try:
                t.system = System.objects.get(pk=system)
            except System.DoesNotExist:
                t.system = System.objects.create(pk=system, name='System #{}'.format(system))
            t.talkgroup_info = talkgroup(tg_dec, t.system)
            if source_default:
                json_source = data.get('source', 0)
                if(json_source > 0):
                    # No need to re add source if its still 0
                    try:
                        source = Source.objects.get(pk=data['source'])
                    except Source.DoesNotExist:
                        source = Source.objects.create(pk=data['source'], description='Source #{}'.format(data['source']))
                    t.source = source
            t.save()
            for unit in data['srcList']:
                try:
                    trans_unit = unit['src']
                except TypeError:
                    trans_unit = unit
                u,created = Unit.objects.get_or_create(dec_id=trans_unit,system=t.system)
                tu = TranmissionUnit.objects.create(transmission=t, unit=u, order=count)
                count=count+1
    else:
        if system_opt >= 0:
            system = system_opt # Command line overrides json
        t.system = System.objects.get(pk=system)
        t.talkgroup_info = talkgroup(tg_dec, t.system)
        t.save()
