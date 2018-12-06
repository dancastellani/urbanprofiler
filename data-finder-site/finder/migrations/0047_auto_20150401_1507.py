# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0046_auto_20150330_1200'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='system',
            options={'ordering': ['-update_time'], 'get_latest_by': 'update_time'},
        ),
        migrations.AlterField(
            model_name='columndata',
            name='value',
            field=models.CharField(max_length=5000),
            preserve_default=True,
        ),
    ]
