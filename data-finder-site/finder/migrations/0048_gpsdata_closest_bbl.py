# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0047_auto_20150401_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpsdata',
            name='closest_bbl',
            field=models.IntegerField(default=1, null=True, blank=True),
            preserve_default=True,
        ),
    ]
