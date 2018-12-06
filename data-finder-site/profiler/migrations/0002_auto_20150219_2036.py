# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='simpletype',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='detailedtype',
            name='dictionary_is_file',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
