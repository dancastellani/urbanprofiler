# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0029_auto_20150112_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='value_length_max',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_length_mean',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_length_min',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_length_std',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_max',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_mean',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_min',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='value_std',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
            preserve_default=True,
        ),
    ]
