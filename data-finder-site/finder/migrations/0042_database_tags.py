# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0041_auto_20150320_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='tags',
            field=models.CharField(max_length=3000, null=True, blank=True),
            preserve_default=True,
        ),
    ]
