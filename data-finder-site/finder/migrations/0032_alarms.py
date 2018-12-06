# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0031_postgis_install_20150218'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=None, max_length=256)),
                ('query', models.CharField(default=None, max_length=256)),
                ('severity', models.CharField(default=2, max_length=256, choices=[(1, b'High'), (2, b'Normal'), (3, b'Low')])),
            ],
            options={
                'ordering': ['severity'],
            },
            bases=(models.Model,),
        ),
    ]
