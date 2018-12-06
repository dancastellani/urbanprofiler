# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseBoundingBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('database_id', models.CharField(max_length=256)),
                ('lat_min', models.DecimalField(max_digits=8, decimal_places=6)),
                ('lat_max', models.DecimalField(max_digits=8, decimal_places=6)),
                ('long_min', models.DecimalField(max_digits=8, decimal_places=6)),
                ('long_max', models.DecimalField(max_digits=8, decimal_places=6)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
