# Generated by Django 3.1.5 on 2021-03-20 19:50

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="profile_pic_url",
            field=models.TextField(blank=True, null=True),
        ),
    ]
