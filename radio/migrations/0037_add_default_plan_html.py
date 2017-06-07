# -*- coding: utf-8 -*-
# 
from __future__ import unicode_literals

from django.db import migrations, models

def set_default_html(apps, schema_editor):
    plans_html = """<h2>Welcome to Trunk-Player</h2>
<p>Currently no plans are setup</p>
                 """

    WebHTML = apps.get_model('radio', 'WebHtml')
    index = WebHTML(name='plans', bodytext=plans_html).save()

def remove_default_html(apps, schema_editor):
    WebHTML = apps.get_model('radio', 'WebHtml')
    WebHTML.objects.filter(name='plans').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0036_auto_20170522_1921'),
    ]

    operations = [
        # Setup a default source
        migrations.RunPython(set_default_html, remove_default_html),
    ]
