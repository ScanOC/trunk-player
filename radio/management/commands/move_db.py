import datetime
import math

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
from django.db import connection

from radio.models import *
from django.db.utils import IntegrityError

table_list = (
    #'auth_group',
    #'auth_group_permissions',
    #'auth_permission',
    'radio_plan',
    'auth_user',
    #'auth_user_groups',
    #'auth_user_user_permissions',
    'account_emailaddress',
    'account_emailconfirmation',
    #'django_admin_log',
    #'django_content_type',
    #'django_migrations',
    #'django_session',
    'sites_site',
    'radio_repeatersite',
    'radio_service',
    'radio_system',
    'radio_agency',
    'radio_source',
    #'radio_profile',
    'radio_siteoption',
    'radio_talkgroup',
    'radio_talkgroupaccess',
    'radio_scanlist',
    'radio_scanlist_talkgroups',
    'radio_menuscanlist',
    'radio_menutalkgrouplist',
    #'radio_tranmissionunit',
    #'radio_transmission',
    'radio_unit',
    'radio_webhtml',
    'radio_siteoption',
    'radio_stripeplanmatrix',
    'socialaccount_socialaccount',
    'socialaccount_socialapp',
    'socialaccount_socialapp_sites',
    'socialaccount_socialtoken',
    )


class Command(BaseCommand):
    help = 'Move all data from the old db into a new one'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--fix-seq', action='store_true', dest='fix-seq', default=False)
        parser.add_argument('-F', '--fix-all-seq', action='store_true', dest='fix-all-seq', default=False)

    def handle(self, *args, **options):
        move_all_db_data(options)



def move_all_db_data(opt):
    global table_list
    db_engine = connection.vendor
    #table_list = ()
    move_data = True
    if opt['fix-seq']:
        table_list = ('radio_transmission',)
        move_data = False
    if opt['fix-all-seq']:
        table_list = table_list + ('radio_transmission',)
        move_data = False
    if move_data == False and db_engine != 'postgresql':
        raise CommandError('Fix Sequance is only used for a postgress database')
    for table_info in table_list:
        tb = table_info.split('_',1)
        app = tb[0]
        table = tb[1]
        if move_data:
            print("Moving data from app {} table {} into new db".format(app,table))
        else:
            print("Fixing postgress for app {} table {} into new db".format(app,table))
        try:
            tb_model = apps.get_model(app_label=app, model_name=table)
        except:
            print("Model {} does not exist, skipping..".format(table))
            continue
        if move_data:
            tb_data = tb_model.objects.using('old').all()
            for rec in tb_data:
                rec.save(using='default')
        if db_engine == 'postgresql':
            with connection.cursor() as cursor:
                update_seq = "SELECT setval(pg_get_serial_sequence('{}', 'id'), coalesce(max(id),0) + 1, false) FROM {};".format(tb_model._meta.db_table, tb_model._meta.db_table)
                #print("Run",update_seq)
                cursor.execute(update_seq)

    if move_data:
        # Now tans
        amount = 5000
        total = Transmission.objects.using('old').count()
        print("Total transmissions",total)
        end_rec = total - 1
        start_rec = end_rec - amount
        start_time = None
        end_time = None
        if start_rec < 0:
          start_rec = 0
        while end_rec > 0:
            run_time = "UNK"
            if end_time:
                #print("End {} Start {} diff {} * ( end {} / total {})".format(end_time, start_time, (end_time - start_time).seconds, end_rec, amount))
                d = divmod((end_time - start_time).seconds * (end_rec / amount ),86400)  # days
                h = divmod(d[1],3600)  # hours
                m = divmod(h[1],60)  # minutes
                s = m[1]  # seconds
                run_time = '{}:{}:{}:{}'.format(math.floor(d[0]),math.floor(h[0]),math.floor(m[0]),math.floor(s)) 
            print('Importing Trans {} to {} Est Run time {}'.format(start_rec,end_rec,run_time))
            start_time = datetime.datetime.now()
            trans = Transmission.objects.using('old').all()[start_rec:end_rec]
            for rec in trans:
                rec.save(using='default')
            end_time = datetime.datetime.now()
            end_rec = end_rec - amount
            start_rec = start_rec - amount
            if start_rec < 0:
                start_rec = 0
        with connection.cursor() as cursor:
            update_seq = "SELECT setval(pg_get_serial_sequence('{}', 'id'), coalesce(max(id),0) + 1, false) FROM {};".format(Transmission._meta.db_table, Transmission._meta.db_table)
            cursor.execute(update_seq)
