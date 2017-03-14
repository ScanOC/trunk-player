# -*- coding: utf-8 -*-
# Save all existing ScanLists to build the new slug
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.text import slugify

def scanlist_slug_build(apps, schema_editor):
    ScanList = apps.get_model('radio', 'ScanList')
    for scanlist in ScanList.objects.all():
        scanlist.slug = slugify(scanlist.name) 
        scanlist.save()

def nothing_to_do(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0029_scanlist_slug'),
    ]

    operations = [
        migrations.RunPython(scanlist_slug_build, nothing_to_do),
    ]
