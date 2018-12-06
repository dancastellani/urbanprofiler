# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0005_auto_20150219_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailedtype',
            name='name',
            field=models.CharField(default=None, max_length=256, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='simpletype',
            name='name',
            field=models.CharField(default=None, max_length=256, unique=True, null=True, blank=True),
            preserve_default=True,
        ),
    ]
