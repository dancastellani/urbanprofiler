# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0044_database_socrata_view_from'),
    ]

    operations = [
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('update_time', models.DateTimeField(auto_now_add=True)),
                ('source_file', models.CharField(default=None, max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
