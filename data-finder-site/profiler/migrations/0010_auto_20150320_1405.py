# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0009_detailedtype_dictionary_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detailedtype',
            name='dictionary_type',
            field=models.CharField(default=b'Equal', max_length=20, choices=[(b'Equal', b'Equal'), (b'Contains', b'Contains')]),
            preserve_default=True,
        ),
    ]
