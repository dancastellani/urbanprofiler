# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0025_database_socrata_update_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='columns_null_count',
            field=models.IntegerField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
