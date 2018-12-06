# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0056_auto_20150702_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='date_max',
            field=models.DateField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='database',
            name='date_min',
            field=models.DateField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
