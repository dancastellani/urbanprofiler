# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0027_auto_20141222_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gpsdata',
            name='lat',
            field=models.DecimalField(max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='long',
            field=models.DecimalField(max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
