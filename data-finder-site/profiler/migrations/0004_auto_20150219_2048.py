# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0003_detailedtype_accept_missing_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailedtype',
            name='execution_order',
            field=models.IntegerField(default=-1, help_text=b'Use an integer positive value 1-based to indicate the order. Ascendent order will be used.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='detailedtype',
            name='accept_missing_values',
            field=models.BooleanField(default=False, help_text=b'Check this if the missing values should be counted on this type.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='detailedtype',
            name='dictionary_is_file',
            field=models.BooleanField(default=False, help_text=b"Check this if the dictionary is on a file on 'resources' folder."),
            preserve_default=True,
        ),
    ]
