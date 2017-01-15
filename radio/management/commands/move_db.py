import datetime
import math

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
from django.db import connection

from radio.models import *
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Move all data from the old db into a new one'

    def handle(self, *args, **options):
        move_all_db_data(options)

def move_all_db_data(opt):
    db_engine = connection.vendor
    table_list = ( 
        'auth_group',
        'auth_group_permissions',
        'auth_permission',
        'radio_plan',
        'auth_user',
        'auth_user_groups',
        'auth_user_user_permissions',
        'account_emailaddress',
        'account_emailconfirmation',
        #'django_admin_log',
        #'django_content_type',
        #'django_migrations',
        #'django_session',
        #'django_site',
        'radio_agency',
        'radio_source',
        #'radio_profile',
        'radio_talkgroup',
        'radio_scanlist',
        'radio_scanlist_talkgroups',
        'radio_menuscanlist',
        'radio_menutalkgrouplist',
        #'radio_tranmissionunit',
        #'radio_transmission',
        'radio_unit',
        'socialaccount_socialaccount',
        'socialaccount_socialapp',
        'socialaccount_socialapp_sites',
        'socialaccount_socialtoken',
        )
    #table_list = ()

    for table_info in table_list:
        tb = table_info.split('_',1)
        app = tb[0]
        table = tb[1]
        print("Moving data from app {} table {} into new db".format(app,table))
        try:
            tb_model = apps.get_model(app_label=app, model_name=table)
        except:
            print("Model {} does not exist, skipping..".format(table))
            continue
        tb_data = tb_model.objects.using('old').all()
        for rec in tb_data:
            rec.save(using='default')
        if db_engine == 'postgresql':
            with connection.cursor() as cursor:
                update_seq = "SELECT setval(pg_get_serial_sequence('{}', 'id'), coalesce(max(id),0) + 1, false) FROM {};".format(tb_model._meta.db_table, tb_model._meta.db_table)
                #print("Run",update_seq)
                cursor.execute(update_seq)


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
        with connection.cursor() as cursor:
            update_seq = "SELECT setval(pg_get_serial_sequence('{}', 'id'), coalesce(max(id),0) + 1, false) FROM {};".format(Transmission._meta.db_table, Transmission._meta.db_table)
            #print("Run",update_seq)
            cursor.execute(update_seq)
        end_time = datetime.datetime.now()
        end_rec = end_rec - amount
        start_rec = start_rec - amount
        if start_rec < 0:
            start_rec = 0
