# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-12 22:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('radio', '0012_auto_20161008_2103'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='transmission',
            name='source',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='radio.Source'),
        ),
    ]
