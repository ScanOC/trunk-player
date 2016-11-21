# -*- coding: utf-8 -*-
# 
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0020_plan_profile'),
    ]

    operations = [
        # Setup a default source
        migrations.RunSQL([("INSERT INTO radio_plan (id,name) VALUES (1,'Member');", None)],
                           [("DELETE FROM radio_plan where id=1;", None)],),
    ]
