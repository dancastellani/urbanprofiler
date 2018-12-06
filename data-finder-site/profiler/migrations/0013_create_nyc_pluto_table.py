# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0012_auto_20150325_2003'),
    ]

    operations = [
        migrations.RunSQL('create table nyc_pluto(\
                                borocode integer, \
                                bbl bigint, \
                                ycoord integer, \
                                xcoord integer, \
                                address text, \
                                borough_acronym text,\
                                lat numeric(9,6), \
                                lon numeric(9,6),\
                                zipcode integer,\
                                borough text  \
                            );',),
        migrations.RunSQL("copy nyc_pluto from '/Files/Documents/projects/auto-etl/src/resources/nyc_pluto_prepared.csv' delimiter ',' csv header;",),
    ]
