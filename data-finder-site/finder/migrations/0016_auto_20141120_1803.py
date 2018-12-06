# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0015_auto_20141120_1742'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'ordering': ['database__id', 'name']},
        ),
        migrations.AlterModelOptions(
            name='database',
            options={'ordering': ['database_id']},
        ),
        migrations.AddField(
            model_name='column',
            name='original',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='profiler_type_most_detected',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='profiler_type_most_detected_percent',
            field=models.DecimalField(default=None, null=True, max_digits=12, decimal_places=10, blank=True),
            preserve_default=True,
        ),
    ]
