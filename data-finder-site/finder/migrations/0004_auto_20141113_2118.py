# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0003_auto_20141113_2009'),
    ]

    operations = [
        migrations.RenameField(
            model_name='databaseinfo',
            old_name='file_name',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='databaseinfo',
            name='socrata_description',
            field=models.TextField(default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
