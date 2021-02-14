# Generated by Django 3.1.5 on 2021-02-14 03:04

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
        ("show", "0001_initial"),
        ("vote", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vote",
            name="show",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="show.show"),
        ),
        migrations.AlterField(
            model_name="vote",
            name="voter",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="user.profile"),
        ),
    ]