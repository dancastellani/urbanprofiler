# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0007_auto_20141114_1849'),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('database_id', models.CharField(max_length=256)),
                ('name', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('category', models.CharField(max_length=256, null=True, blank=True)),
                ('owner', models.CharField(max_length=256, null=True, blank=True)),
                ('author', models.CharField(max_length=256, null=True, blank=True)),
                ('profiler_input_file', models.CharField(max_length=256, null=True, blank=True)),
                ('profiler_status', models.CharField(max_length=256, null=True, blank=True)),
                ('profiler_time_begin', models.CharField(max_length=256, null=True, blank=True)),
                ('profiler_time_end', models.CharField(max_length=256, null=True, blank=True)),
                ('socrata_status', models.CharField(max_length=256, null=True, blank=True)),
                ('socrata_download_count', models.IntegerField(null=True, blank=True)),
                ('socrata_view_count', models.IntegerField(null=True, blank=True)),
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
                ('lat_min', models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True)),
                ('lat_max', models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True)),
                ('long_min', models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True)),
                ('long_max', models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True)),
            ],
            options={
                'ordering': ['database_id', 'category', 'owner', 'author', 'rows', 'columns_count'],
                'verbose_name': 'Database',
                'verbose_name_plural': 'Databases',
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='DatabaseInfo',
        ),
    ]
