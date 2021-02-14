# Generated by Django 3.0.6 on 2021-01-20 19:43

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0001_initial"),
        ("comment", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Read",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now=True)),
                (
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="reads", to="comment.Comment"
                    ),
                ),
                (
                    "reader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="read_comments", to="user.Profile"
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("reader", "comment")},
            },
        ),
    ]