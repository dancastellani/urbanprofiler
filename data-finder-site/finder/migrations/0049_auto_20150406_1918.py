# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0048_gpsdata_closest_bbl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='profiler_type_most_detected_percent',
            field=models.DecimalField(default=None, null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='lat_max',
            field=models.DecimalField(default=None, null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='lat_min',
            field=models.DecimalField(default=None, null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='long_max',
            field=models.DecimalField(default=None, null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='long_min',
            field=models.DecimalField(default=None, null=True, max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='profiler_input_file_size',
            field=models.DecimalField(default=None, null=True, max_digits=16, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='closest_bbl',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='lat',
            field=models.DecimalField(max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='long',
            field=models.DecimalField(max_digits=9, decimal_places=6, blank=True),
            preserve_default=True,
        ),
    ]
