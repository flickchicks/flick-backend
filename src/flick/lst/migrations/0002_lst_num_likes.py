# Generated by Django 3.0.6 on 2021-01-29 22:48

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("lst", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="lst", name="num_likes", field=models.IntegerField(default=0, null=True),),
    ]
