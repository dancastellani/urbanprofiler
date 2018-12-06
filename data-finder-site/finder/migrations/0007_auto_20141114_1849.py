# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0006_auto_20141113_2207'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='databaseinfo',
            options={'ordering': ['database_id', 'category', 'owner', 'author', 'rows', 'columns_count'], 'verbose_name': 'Database', 'verbose_name_plural': 'Databases'},
        ),
        migrations.RenameField(
            model_name='databaseinfo',
            old_name='socrata_author',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='databaseinfo',
            old_name='socrata_category',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='databaseinfo',
            old_name='socrata_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='databaseinfo',
            old_name='socrata_owner',
            new_name='owner',
        ),
    ]
