# Generated by Django 3.1.5 on 2022-03-11 00:45

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("reaction", "0005_alter_reaction_visibility"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reaction",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]