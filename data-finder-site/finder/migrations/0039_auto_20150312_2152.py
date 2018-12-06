# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0038_alarm_target'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColumnData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(default=None, max_length=256)),
                ('key', models.CharField(max_length=256, db_index=True)),
                ('value', models.CharField(max_length=256)),
                ('column', models.ForeignKey(to='finder.Column')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='alarm',
            options={'ordering': ['severity', '-count', 'name']},
        ),
    ]
