# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0008_auto_20150226_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailedtype',
            name='dictionary_type',
            field=models.CharField(default=b'Equal', max_length=20, choices=[(b'Equal', b'Equal'), (b'Like', b'Like')]),
            preserve_default=True,
        ),
    ]
