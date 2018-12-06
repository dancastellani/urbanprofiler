# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0059_auto_20150716_1321'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='gpsdata',
            index_together=set([('lat', 'long')]),
        ),
    ]
