# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0032_alarms'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alarms',
            options={'ordering': ['severity', 'name']},
        ),
        migrations.AlterField(
            model_name='alarms',
            name='name',
            field=models.CharField(default=None, unique=True, max_length=256),
            preserve_default=True,
        ),
    ]
