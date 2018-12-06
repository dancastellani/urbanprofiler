# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0004_auto_20141113_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databaseinfo',
            name='lat_max',
            field=models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='databaseinfo',
            name='lat_min',
            field=models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='databaseinfo',
            name='long_max',
            field=models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='databaseinfo',
            name='long_min',
            field=models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
