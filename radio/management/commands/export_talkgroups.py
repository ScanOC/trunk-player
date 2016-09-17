import sys
import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *

class Command(BaseCommand):
    help = 'Import talkgroup info'

    def add_arguments(self, parser):
        parser.add_argument('file')

    def handle(self, *args, **options):
        f_name = options['file']
        export_tg_file(f_name)


def export_tg_file(file_name):
    ''' Using the talkgroup file from trunk-recorder'''
    talkgroups = TalkGroup.objects.all()
    with open(file_name, "w") as tg_file:
        for t in talkgroups:
            alpha = t.alpha_tag
            description = t.description
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
            tg_file.write("{},0x00,A,{},{},,3,{}\n".format(t.dec_id,alpha,description,common))

