# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0002_auto_20141111_2305'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('database_id', models.CharField(max_length=256)),
                ('file_name', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('profiler_input_file', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('profiler_status', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('profiler_time_begin', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('profiler_time_end', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_status', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_description', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_category', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_owner', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_author', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_download_count', models.IntegerField(default=None, null=True, blank=True)),
                ('socrata_view_count', models.IntegerField(default=None, null=True, blank=True)),
                ('rows', models.IntegerField(default=None, null=True, blank=True)),
                ('missing_rows', models.IntegerField(default=None, null=True, blank=True)),
                ('columns_count', models.IntegerField(default=None, null=True, blank=True)),
                ('columns_geo_count', models.IntegerField(default=None, null=True, blank=True)),
                ('columns_numeric_count', models.IntegerField(default=None, null=True, blank=True)),
                ('columns_temporal_count', models.IntegerField(default=None, null=True, blank=True)),
                ('columns_text_count', models.IntegerField(default=None, null=True, blank=True)),
                ('values', models.IntegerField(default=None, null=True, blank=True)),
                ('values_missing', models.IntegerField(default=None, null=True, blank=True)),
                ('gps_values', models.IntegerField(default=None)),
                ('lat_min', models.DecimalField(max_digits=12, decimal_places=10)),
                ('lat_max', models.DecimalField(max_digits=12, decimal_places=10)),
                ('long_min', models.DecimalField(max_digits=12, decimal_places=10)),
                ('long_max', models.DecimalField(max_digits=12, decimal_places=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='DatabaseBoundingBox',
        ),
    ]
