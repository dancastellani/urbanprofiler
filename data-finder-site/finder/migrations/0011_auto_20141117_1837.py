# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0010_database_socrata_primary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='database',
            name='gps_values',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
