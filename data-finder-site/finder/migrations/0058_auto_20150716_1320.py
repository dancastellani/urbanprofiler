# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0057_auto_20150715_1220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gpsdata',
            name='epoch_secs',
        ),
        migrations.RemoveField(
            model_name='gpsdata',
            name='hour',
        ),
    ]
