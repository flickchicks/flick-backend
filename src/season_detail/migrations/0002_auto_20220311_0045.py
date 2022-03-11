# Generated by Django 3.1.5 on 2022-03-11 00:45

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("season_detail", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="seasondetail",
            name="is_default",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name="seasondetail",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
