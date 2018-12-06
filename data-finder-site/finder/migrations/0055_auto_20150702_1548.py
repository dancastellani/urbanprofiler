# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0054_gpsdata_db'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpsdata',
            name='day',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gpsdata',
            name='epoch_secs',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gpsdata',
            name='hour',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gpsdata',
            name='month',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gpsdata',
            name='year',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
    ]
