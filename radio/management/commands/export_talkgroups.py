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
            help='Export talkgroups from only this system',
        )


    def handle(self, *args, **options):
        export_tg_file(self, options)


def export_tg_file(self, options):
    ''' Using the talkgroup file from trunk-recorder'''
    file_name = options['file']
    system = options['system']
    talkgroups = TalkGroup.objects.all()
    if system >= 0:
        talkgroups = talkgroups.filter(system=system)
        self.stdout.write("Exporting talkgroups for system #{}".format(system))
    else:
        self.stdout.write("Exporting talkgroups for all systems")
    with open(file_name, "w") as tg_file:
        for t in talkgroups:
            alpha = t.alpha_tag
            description = t.description
            hex_val = str(hex(t.dec_id))[2:-1].zfill(3)
            try:
                alpha = alpha.rstrip()
            except AttributeError:
                pass
            try:
                description = description.rstrip()
            except AttributeError:
                pass
            common = ''
            if(t.common_name):
                common = t.common_name
            service_type = ''
            if(t.service_type):
                service_type = t.service_type
            home_site = ''
            if(t.home_site):
                home_site = t.home_site
            systemid = ''
            if(t.system_id):
                systemid = t.system_id
            tg_file.write("{},{},{},{},{},{},{},{},{}\n".format(t.dec_id,hex_val,t.mode,alpha,description,service_type,home_site,systemid,t.priority))

