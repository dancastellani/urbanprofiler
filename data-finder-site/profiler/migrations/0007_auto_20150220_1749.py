# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0006_auto_20150219_2101'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detailedtype',
            old_name='execution_order',
            new_name='order_in_type',
        ),
        migrations.AddField(
            model_name='simpletype',
            name='global_order',
            field=models.IntegerField(default=0, help_text=b'Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.'),
            preserve_default=False,
        ),
    ]
