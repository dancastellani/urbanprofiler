# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0053_auto_20150429_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpsdata',
            name='db',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
