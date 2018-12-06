# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0014_auto_20141119_1921'),
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('profiler_type', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('socrata_type', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('values', models.IntegerField(default=None, null=True, blank=True)),
                ('unique', models.IntegerField(default=None, null=True, blank=True)),
                ('missing', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_geo', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_temporal', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_numeric', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_geo_gps', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_geo_zip', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_geo_zip_9', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_geo_borough', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_temporal_date', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_temporal_time', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_temporal_datetime', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_numeric_double', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_numeric_int', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_textual', models.IntegerField(default=None, null=True, blank=True)),
                ('type_count_null', models.IntegerField(default=None, null=True, blank=True)),
                ('database', models.ForeignKey(to='finder.Database')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='database',
            options={'ordering': ['database_id'], 'verbose_name': 'Database', 'verbose_name_plural': 'Databases'},
        ),
    ]
