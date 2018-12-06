# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0049_auto_20150406_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpsdata',
            name='address',
            field=models.CharField(max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gpsdata',
            name='borough',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gpsdata',
            name='zipcode',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='lat',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='long',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
    ]
