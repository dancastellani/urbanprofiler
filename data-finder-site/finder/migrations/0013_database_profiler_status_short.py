# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0012_auto_20141118_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='profiler_status_short',
            field=models.CharField(max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
    ]
