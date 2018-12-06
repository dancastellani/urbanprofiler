# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0019_auto_20141201_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='LatLongData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.DecimalField(max_digits=12, decimal_places=10, blank=True)),
                ('long', models.DecimalField(max_digits=12, decimal_places=10, blank=True)),
                ('count', models.IntegerField(default=1, null=True, blank=True)),
                ('database', models.ForeignKey(to='finder.Database')),
            ],
            options={
                'ordering': ['database__id', 'lat', 'long'],
            },
            bases=(models.Model,),
        ),
    ]
