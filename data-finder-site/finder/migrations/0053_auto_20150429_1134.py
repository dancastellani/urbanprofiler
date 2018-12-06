# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0052_auto_20150423_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 15, 34, 7, 741730, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='column',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 15, 34, 15, 469666, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='database',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 15, 34, 22, 709406, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='database',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 15, 34, 24, 605325, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
