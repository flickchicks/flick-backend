# Generated by Django 3.1.5 on 2022-03-12 08:46

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reaction", "0007_reaction_num_likes"),
        ("like", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="like",
            name="reaction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likers",
                to="reaction.reaction",
            ),
        ),
    ]
