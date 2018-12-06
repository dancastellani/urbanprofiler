# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0013_create_nyc_pluto_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailedtype',
            name='dictionary_type',
            field=models.CharField(default=b'Equal', max_length=20, choices=[(b'Equal', b'Equal'), (b'Contains', b'Contains'), (b'Contains Word', b'Contains Word')]),
            preserve_default=True,
        ),
    ]
