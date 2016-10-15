# -*- coding: utf-8 -*-
# 
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0015_auto_20161014_2051'),
    ]

    operations = [
        # Setup a default source
        migrations.RunSQL([("INSERT INTO radio_agency (id,name,short) VALUES (0,'Default','_DEF_');", None)],
                           [("DELETE FROM radio_agency where id=0;", None)],),
    ]
