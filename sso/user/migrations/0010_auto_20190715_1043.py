# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-15 10:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20190715_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='job_title',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
