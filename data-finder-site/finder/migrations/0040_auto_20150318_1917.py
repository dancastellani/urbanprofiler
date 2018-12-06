# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0039_auto_20150312_2152'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='columndata',
            options={'ordering': ['column', 'group', 'key']},
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_geo',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_geo_borough',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_geo_gps',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_geo_zip',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_geo_zip_9',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_null',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_numeric',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_numeric_double',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_numeric_int',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_temporal',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_temporal_date',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_temporal_datetime',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_temporal_time',
        ),
        migrations.RemoveField(
            model_name='column',
            name='type_count_textual',
        ),
    ]
