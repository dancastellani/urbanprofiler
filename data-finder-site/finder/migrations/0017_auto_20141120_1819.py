# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0016_auto_20141120_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='profiler_type_most_detected_percent',
            field=models.DecimalField(default=None, null=True, max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
