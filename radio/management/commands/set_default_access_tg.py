import sys
import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from radio.models import *

class Command(BaseCommand):
    help = 'Helper for new TalkGroup Access'

    def add_arguments(self, parser):
        parser.add_argument('access_group_name')


    def handle(self, *args, **options):
        access_menu(self, options)

def access_menu(self, options):
    try:
        access_gp = TalkGroupAccess.objects.get(name=options['access_group_name'])
    except TalkGroupAccess.DoesNotExist:
        self.stdout.write(self.style.ERROR('Talk Group Access List [{}] does not exist, check case and spelling'.format(options['access_group_name'])))
        all_access_names = TalkGroupAccess.objects.all()
        if all_access_names:
            self.stdout.write('Current Talk Group Access lists in the database:')
            for tg in all_access_names:
                self.stdout.write(tg.name)
        else:
            self.stdout.write(self.style.ERROR('**There are no Talk Group Access lists in the database'))
        return
    self.stdout.write('Setting all current public Talk Groups into {}'.format(access_gp.name))
    ct=0
    for tg in TalkGroupWithSystem.objects.filter(public=True):
        access_gp.talkgroups.add(tg)
        ct += 1
    self.stdout.write(self.style.SUCCESS('Added {} TalkGroups to Talk Group Access List - {}'.format(ct, access_gp.name)))
