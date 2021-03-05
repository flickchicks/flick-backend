# Generated by Django 3.1.5 on 2021-03-05 06:20

from django.conf import settings
from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("comment", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lst", "0001_initial"),
        ("user", "0001_initial"),
        ("show", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Discover",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "friend_comments",
                    models.ManyToManyField(blank=True, related_name="friend_comment", to="comment.Comment"),
                ),
                ("friend_lsts", models.ManyToManyField(blank=True, related_name="friend_lst_recommend", to="lst.Lst")),
                (
                    "friend_recommendations",
                    models.ManyToManyField(blank=True, related_name="profile_recommend", to="user.Profile"),
                ),
                (
                    "friend_shows",
                    models.ManyToManyField(blank=True, related_name="friend_show_recommend", to="show.Show"),
                ),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
