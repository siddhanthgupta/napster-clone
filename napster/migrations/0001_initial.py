# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-12 14:26
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('port', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(65535), django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('ip_address', 'port')]),
        ),
    ]