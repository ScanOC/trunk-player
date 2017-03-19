# -*- coding: utf-8 -*-
# Save default html text for index and about page
from __future__ import unicode_literals

from django.db import migrations, models

def set_default_html(apps, schema_editor):
    index_html = """<h1>Welcome to Trunk-Player</h1>
<p>
  This is the new way to listen to public safety radio traffic. Many other sites allow you to live stream audio feeds from a radio scanner. This site is different from all the rest.
</p>
<p>
  We give you full control of which talkgroups/frequencies you want to hear. We also time shift (like a DVR) the transmissions. When two transmissions overlap using a standard scanner or streaming site you will only hear one, then you will scan into the second one in progresss, not here. The site will play the first transmission and when that is complete it will start to play the second transmission from the beginning, this is time shifting like a DVR.
</p>
<h2>
  Getting started
</h2>
<p>
  Jump right into the <a href="/scan/default/">Main Scan List</a>.
</p> """

    about_html = """<h2>About Trunk-Player</h2>
<p>This is the new way to listen to your local public safety radio system. Many other sites allow you to live stream audio feeds from a radio scanner. This site is different from all the rest.</p>
<p><strong>Features :</strong></p>
<ul>
  <li>You select the talk groups or scan lists you want to listen to</li>
  <li>History, you can listen to radio traffic from the past</li>
  <li>View which unit is transmitting</li>
  <li>Concurrent recording of multiple transmissions, you will not miss any of the action</li>
</ul> """

    WebHTML = apps.get_model('radio', 'WebHtml')
    index = WebHTML(name='index', bodytext=index_html).save()
    about = WebHTML(name='about', bodytext=about_html).save()

def nothing_to_do(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0031_webhtml'),
    ]

    operations = [
        migrations.RunPython(set_default_html, nothing_to_do),
    ]
