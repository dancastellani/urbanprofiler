# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0030_auto_20150112_2049'),
    ]

    operations = [
        # migrations.RunSQL('select 1 from finder_database',),
        migrations.RunSQL('CREATE EXTENSION postgis;',),
        migrations.RunSQL('CREATE EXTENSION fuzzystrmatch;',),
        migrations.RunSQL('CREATE EXTENSION postgis_tiger_geocoder;',),
        
    ]
