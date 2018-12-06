# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0043_auto_20150324_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='socrata_view_from',
            field=models.CharField(max_length=20, null=True),
            preserve_default=True,
        ),
    ]
