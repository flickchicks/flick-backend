# Generated by Django 3.1.5 on 2022-03-14 01:03

from django.db import migrations
from django.db import models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("reaction", "0006_auto_20220311_0045"),
    ]

    operations = [
        migrations.AddField(
            model_name="reaction",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(model_name="reaction", name="updated_at", field=models.DateTimeField(auto_now=True),),
    ]
