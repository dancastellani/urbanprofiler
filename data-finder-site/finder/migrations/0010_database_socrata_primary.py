# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0009_auto_20141117_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='socrata_primary',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
