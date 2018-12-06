# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0011_auto_20141117_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='database',
            name='missing_rows',
        ),
        migrations.AddField(
            model_name='database',
            name='socrata_unique_key',
            field=models.CharField(max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='gps_values',
            field=models.IntegerField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
