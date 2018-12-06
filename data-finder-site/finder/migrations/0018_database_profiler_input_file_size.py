# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0017_auto_20141120_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='profiler_input_file_size',
            field=models.DecimalField(default=None, null=True, max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
