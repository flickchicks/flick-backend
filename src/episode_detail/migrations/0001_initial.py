# Generated by Django 3.2.11 on 2022-02-18 01:52

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EpisodeDetail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ext_api_id", models.IntegerField(blank=True, null=True)),
                ("episode_num", models.IntegerField(blank=True, null=True)),
                ("name", models.TextField(blank=True, null=True)),
                ("overview", models.TextField(blank=True, null=True)),
            ],
        ),
    ]