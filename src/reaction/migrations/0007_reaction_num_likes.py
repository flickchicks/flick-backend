# Generated by Django 3.1.5 on 2022-03-12 08:46

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reaction", "0006_auto_20220311_0045"),
    ]

    operations = [
        migrations.AddField(model_name="reaction", name="num_likes", field=models.IntegerField(default=0, null=True),),
    ]