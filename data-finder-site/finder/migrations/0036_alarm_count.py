# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0035_auto_20150227_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarm',
            name='count',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
