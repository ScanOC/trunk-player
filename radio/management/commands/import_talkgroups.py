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
        parser.add_argument(
            '--system',
            type=int,
            help='System that this import is for',
            required=True,
        )
        parser.add_argument(
            '--truncate',
            dest='truncate',
            action='store_true',
            help='Truncat any data that would not fit into the DB',
            default=True,
       )
        parser.add_argument(
            '--rr',
            dest='rr',
            action='store_true',
            help='Import in Radio Refrence Format',
            default=False,
       )
        parser.add_argument(
            '--update',
            dest='update',
            action='store_true',
            help='Update existing records in the database',
            default=False,
       )

    def handle(self, *args, **options):
        import_tg_file(self, options)


def import_tg_file(self, options):
    ''' Using the talkgroup file from trunk-recorder'''
    file_name = options['file']
    system_id = options['system']
    truncate = options['truncate']
    rrFormat = options['rr']
    update = options['update']
    try:
        system = System.objects.get(pk=system_id)
    except System.DoesNotExist:
        self.stdout.write("Valid systems")
        for system in System.objects.all():
            self.stdout.write("#{} - {}".format(system.pk, system.name))
        raise CommandError('System #{} was not a valid system'.format(system_id))
    self.stdout.write("Importing talkgroups for system #{} - {}".format(system.pk, system.name))
    if truncate:
      mode_max_length = TalkGroup._meta.get_field('mode').max_length
      alpha_tag_max_length = TalkGroup._meta.get_field('alpha_tag').max_length
      description_max_length = TalkGroup._meta.get_field('description').max_length
    with open(file_name) as tg_file:
        tg_info = csv.reader(tg_file, delimiter=',', quotechar='"')
        line_number = 0
        if not rrFormat:
            for row in tg_info:
                line_number+=1
                try:
                    if truncate:
                        if len(row[2]) > mode_max_length:
                            row[2] = row[2][:mode_max_length]
                            self.stdout.write("Truncating mode from line ({}) TG {}".format(line_number, row[3]))
                        if len(row[3]) > alpha_tag_max_length:
                            row[3] = row[3][:alpha_tag_max_length]
                            self.stdout.write("Truncating alpha_tag from line ({}) TG {}".format(line_number, row[3]))
                        if len(row[4]) > description_max_length:
                            row[4] = row[4][:description_max_length]
                            self.stdout.write("Truncating description from line ({}) TG {}".format(line_number, row[3]))
                    #print('LEN ' + str(len(row)))
                    priority = 3
                    try:
                        priority = row[7]
                    except IndexError:
                        pass
                    try:
                        priority = int(priority)
                    except ValueError:
                        priority = 3
                    obj, create = TalkGroup.objects.update_or_create(dec_id=row[0], system=system, defaults={'mode': row[2], 'alpha_tag': row[3], 'description': row[4], 'priority': priority})
                    if not create and options['update']:
                      obj.mode = row[2]
                      obj.alpha_tag = row[3]
                      obj.description = row[4]
                      obj.priority = priority
                      obj.save()
                    obj.service_type = row[5][:20]
                    obj.save()
                except (IntegrityError, IndexError):
                    pass
                    #print("Skipping {}".format(row[3]))
        else:
            for row in tg_info:
                line_number+=1
                try:
                    if truncate:
                        if len(row[3]) > mode_max_length:
                            row[3] = row[3][:mode_max_length]
                            self.stdout.write("Truncating mode from line ({}) TG {}".format(line_number, row[2]))
                        if len(row[2]) > alpha_tag_max_length:
                            row[2] = row[2][:alpha_tag_max_length]
                            self.stdout.write("Truncating alpha_tag from line ({}) TG {}".format(line_number, row[2]))
                        if len(row[4]) > description_max_length:
                            row[4] = row[4][:description_max_length]
                            self.stdout.write("Truncating description from line ({}) TG {}".format(line_number, row[2]))
                    #print('LEN ' + str(len(row)))
                    priority = 3
                    obj, create = TalkGroup.objects.update_or_create(dec_id=row[0], system=system, defaults={'mode': row[3], 'alpha_tag': row[2], 'description': row[4], 'priority': priority})
                    if not create and options['update']:
                      obj.mode = row[2]
                      obj.alpha_tag = row[3]
                      obj.description = row[4]
                      obj.priority = priority
                      obj.save()
                    obj.service_type = row[5][:20]
                    obj.save()
                except (IntegrityError, IndexError, ValueError):
                    pass
                    #print("Skipping {}".format(row[3]))
