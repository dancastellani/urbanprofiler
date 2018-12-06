# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0024_auto_20141218_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='socrata_update_frequency',
            field=models.CharField(max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
    ]
