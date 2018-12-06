# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0068_database_access_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='hue_status',
            field=models.CharField(default=b'enable', max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
