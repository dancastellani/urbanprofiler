# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0063_database_source_agency'),
    ]

    operations = [
        migrations.RunSQL('drop materialized view finder_view_index_temp;',),
        migrations.AlterField(
            model_name='alarm',
            name='query',
            field=models.CharField(default=None, max_length=1000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='db',
            field=models.CharField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunSQL('create materialized view finder_view_index_temp as \
                             SELECT db, year, month, day, sum(count) AS count \
                             FROM finder_gpsdata \
                             WHERE year IS NOT NULL AND db IS NOT NULL \
                             GROUP BY db, year, month, day;',),
    ]
