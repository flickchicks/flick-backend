# Generated by Django 3.1.5 on 2021-03-05 23:36

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tag", "0001_initial"),
        ("show", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lst",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("pic", models.TextField(blank=True, null=True)),
                ("is_saved", models.BooleanField(default=False, null=True)),
                ("is_private", models.BooleanField(default=False, null=True)),
                ("is_watch_later", models.BooleanField(default=False, null=True)),
                ("description", models.CharField(blank=True, default="", max_length=150, null=True)),
                ("num_likes", models.IntegerField(default=0, null=True)),
                ("collaborators", models.ManyToManyField(blank=True, related_name="collab_lsts", to="user.Profile")),
                ("custom_tags", models.ManyToManyField(blank=True, related_name="lsts", to="tag.Tag")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="owner_lsts", to="user.profile"
                    ),
                ),
                ("shows", models.ManyToManyField(blank=True, to="show.Show")),
            ],
        ),
    ]
