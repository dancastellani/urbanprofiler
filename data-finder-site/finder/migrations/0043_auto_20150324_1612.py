# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0042_database_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'ordering': ['database', 'name']},
        ),
    ]
