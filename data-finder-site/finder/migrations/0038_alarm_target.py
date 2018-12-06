# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0037_auto_20150227_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='target',
            field=models.CharField(default=b'finder_column', max_length=256, choices=[(b'finder_column', b'Column'), (b'finder_database', b'Dataset')]),
            preserve_default=True,
        ),
    ]
