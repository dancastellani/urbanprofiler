# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databaseboundingbox',
            name='lat_max',
            field=models.DecimalField(max_digits=12, decimal_places=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='databaseboundingbox',
            name='lat_min',
            field=models.DecimalField(max_digits=12, decimal_places=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='databaseboundingbox',
            name='long_max',
            field=models.DecimalField(max_digits=12, decimal_places=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='databaseboundingbox',
            name='long_min',
            field=models.DecimalField(max_digits=12, decimal_places=10),
            preserve_default=True,
        ),
    ]
