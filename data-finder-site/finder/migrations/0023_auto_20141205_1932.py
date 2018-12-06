# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0022_auto_20141205_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='top_value',
            field=models.CharField(default=None, max_length=3000, null=True, blank=True),
            preserve_default=True,
        ),
    ]
