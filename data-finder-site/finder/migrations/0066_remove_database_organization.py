# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0065_auto_20150903_1706'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='database',
            name='organization',
        ),
    ]
