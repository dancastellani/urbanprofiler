# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0036_alarm_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='profiler_type_most_detected',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
    ]
