# Generated by Django 3.0.6 on 2021-04-08 22:41

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("show", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="show", name="trailer_keys", field=models.TextField(blank=True, null=True),),
    ]
