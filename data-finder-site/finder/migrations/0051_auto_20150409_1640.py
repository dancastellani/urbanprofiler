# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0050_auto_20150409_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gpsdata',
            name='address',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
