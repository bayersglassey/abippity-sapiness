# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-05 06:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='public_read',
            field=models.BooleanField(default=False, verbose_name='Public (Readable)'),
        ),
        migrations.AddField(
            model_name='document',
            name='public_write',
            field=models.BooleanField(default=False, verbose_name='Public (Writable)'),
        ),
        migrations.AddField(
            model_name='document',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]