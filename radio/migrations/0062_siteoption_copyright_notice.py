# -*- coding: utf-8 -*-
# Save default html text for index and about page
from __future__ import unicode_literals

from django.db import migrations, models

def set_default_html(apps, schema_editor):

    SiteOption = apps.get_model('radio', 'SiteOption')
    SiteOption(name='COPYRIGHT_NOTICE', 
               value = 'Copyright 2019',
               javascript_visible = True,
               template_visible = True,
               description = 'Edit to update Copyright notice',
              ).save()

def nothing_to_do(apps, schema_editor):
    SiteOption = apps.get_model('radio', 'SiteOption')
    SiteOption.objects.get(name='COPYRIGHT_NOTICE').delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('radio', '0061_transmission_has_audio'),
    ]

    operations = [
        migrations.RunPython(set_default_html, nothing_to_do),
    ]
