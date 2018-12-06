# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0026_database_columns_null_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='database',
            name='lat_max',
            field=models.DecimalField(default=None, null=True, max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='lat_min',
            field=models.DecimalField(default=None, null=True, max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='long_max',
            field=models.DecimalField(default=None, null=True, max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='long_min',
            field=models.DecimalField(default=None, null=True, max_digits=13, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
