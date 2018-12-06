# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0058_auto_20150716_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gpsdata',
            name='day',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='month',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='year',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='gpsdata',
            index_together=set([('lat', 'long'), ('year', 'month', 'day')]),
        ),
    ]
