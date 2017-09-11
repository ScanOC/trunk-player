# -*- coding: utf-8 -*-
# Save default html text for index and about page
from __future__ import unicode_literals

from django.db import migrations, models

def set_default_html(apps, schema_editor):

    SiteOption = apps.get_model('radio', 'SiteOption')
    SiteOption(name='SEND_ADMIN_EMAIL_ON_NEW_USER', 
               value = 'False',
               javascript_visible = False,
               template_visible = False,
               description = 'Send email to admin user when new user registers',
              ).save()

def nothing_to_do(apps, schema_editor):
    SiteOption = apps.get_model('radio', 'SiteOption')
    SiteOption.objects.get(name='SEND_ADMIN_EMAIL_ON_NEW_USER').delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('radio', '0044_siteoption'),
    ]

    operations = [
        migrations.RunPython(set_default_html, nothing_to_do),
    ]
