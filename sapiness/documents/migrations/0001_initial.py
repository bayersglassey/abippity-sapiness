# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-04 22:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('content', models.TextField(verbose_name='Content')),
            ],
        ),
    ]
