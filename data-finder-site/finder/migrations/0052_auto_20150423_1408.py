# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0051_auto_20150409_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='name',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='value_max',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='value_min',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='author',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='category',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='description',
            field=models.TextField(db_index=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='gps_values',
            field=models.IntegerField(default=None, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='name',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='owner',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='profiler_status',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='profiler_status_short',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='socrata_created_at',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='socrata_primary',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='socrata_status',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='database',
            name='tags',
            field=models.CharField(db_index=True, max_length=3000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='address',
            field=models.CharField(db_index=True, max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='borough',
            field=models.CharField(db_index=True, max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='zipcode',
            field=models.CharField(db_index=True, max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='gpsdata',
            index_together=set([('lat', 'long')]),
        ),
    ]
