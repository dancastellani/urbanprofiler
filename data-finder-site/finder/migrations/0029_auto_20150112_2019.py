# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0028_auto_20141222_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='type_count_geo',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_null',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_numeric',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_temporal',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='column',
            name='type_count_textual',
            field=models.DecimalField(default=None, null=True, max_digits=6, decimal_places=3, blank=True),
            preserve_default=True,
        ),
    ]
