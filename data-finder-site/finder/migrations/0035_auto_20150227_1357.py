# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0034_auto_20150226_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alarm',
            name='severity',
            field=models.CharField(default=b'2', max_length=256, choices=[(b'1', b'High'), (b'2', b'Normal'), (b'3', b'Low')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='profiler_type',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='socrata_type',
            field=models.CharField(default=None, max_length=256, null=True, db_index=True, blank=True),
            preserve_default=True,
        ),
    ]
