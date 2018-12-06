# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0011_auto_20150324_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailedtype',
            name='color',
            field=models.CharField(default=b'#FFF', max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='simpletype',
            name='color',
            field=models.CharField(default=b'#FFF', max_length=20),
            preserve_default=True,
        ),
    ]
