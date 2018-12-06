# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0007_auto_20150220_1749'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detailedtype',
            options={'ordering': ['order_in_type', 'name']},
        ),
        migrations.AlterModelOptions(
            name='simpletype',
            options={'ordering': ['global_order', 'name']},
        ),
        migrations.AlterField(
            model_name='detailedtype',
            name='values_dictionary',
            field=models.CharField(help_text=b'in CSV format. Use double quotes for values with space.', max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
    ]
