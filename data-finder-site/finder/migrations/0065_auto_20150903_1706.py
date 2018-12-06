# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0064_auto_20150818_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='organization',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gpsdata',
            name='zipcode',
            field=models.CharField(db_index=True, max_length=21, null=True, blank=True),
            preserve_default=True,
        ),
    ]
