# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0010_auto_20150320_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailedtype',
            name='order_in_type_presentation',
            field=models.IntegerField(default=0, help_text=b'Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='simpletype',
            name='global_order_presentation',
            field=models.IntegerField(default=0, help_text=b'Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.'),
            preserve_default=False,
        ),
    ]
