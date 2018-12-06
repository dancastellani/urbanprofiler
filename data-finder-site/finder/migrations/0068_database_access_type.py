# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0067_database_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='access_type',
            field=models.CharField(default=b'Open', max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
