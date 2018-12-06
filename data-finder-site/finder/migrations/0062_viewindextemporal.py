# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0061_auto_20150716_1727'),
    ]

    operations = [
        migrations.RunSQL('create materialized view finder_view_index_temp as \
                            # SELECT db, year, month, day, sum(count) AS count \
                            # FROM finder_gpsdata \
                            # WHERE year IS NOT NULL AND db IS NOT NULL \
                            # GROUP BY db, year, month, day;',),
        migrations.CreateModel(
            name='ViewIndexTemporal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('day', models.IntegerField()),
                ('count', models.IntegerField()),
            ],
            options={
                'ordering': ['year', 'month', 'day'],
                'db_table': 'view_index_temp',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
