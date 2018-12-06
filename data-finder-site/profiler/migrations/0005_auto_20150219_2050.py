# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0004_auto_20150219_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailedtype',
            name='execution_order',
            field=models.IntegerField(help_text=b'Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.'),
            preserve_default=True,
        ),
    ]
