# -*- coding: utf-8 -*-
# 
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0022_system'),
    ]

    operations = [
        # Setup a default source
        migrations.RunSQL([("INSERT INTO radio_system (id,name) VALUES (0,'Default');", None)],
                           [("DELETE FROM radio_agency where id=0;", None)],),
    ]
