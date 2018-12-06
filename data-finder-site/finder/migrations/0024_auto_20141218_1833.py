# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0023_auto_20141205_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='type_count_geo_borough',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_geo_gps',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_geo_zip',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_geo_zip_9',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_numeric_double',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_numeric_int',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_temporal_date',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_temporal_datetime',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_temporal_time',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
    ]
