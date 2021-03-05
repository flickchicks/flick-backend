# Generated by Django 3.1.5 on 2021-03-05 00:06

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0001_initial"),
        ("show", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Vote",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "choice",
                    models.CharField(
                        blank=True, choices=[("Y", "yes"), ("N", "no"), ("M", "maybe")], max_length=1, null=True
                    ),
                ),
                ("show", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="show.show")),
                ("voter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="user.profile")),
            ],
        ),
    ]
