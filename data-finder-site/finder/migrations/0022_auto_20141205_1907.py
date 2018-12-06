# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0021_auto_20141202_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='top_freq',
            field=models.IntegerField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='top_value',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
    ]
