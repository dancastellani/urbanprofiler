# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0040_auto_20150318_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='columndata',
            name='value',
            field=models.CharField(max_length=3000),
            preserve_default=True,
        ),
    ]
