# Generated by Django 3.1.5 on 2021-03-05 23:52

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
                        on_delete=django.db.models.deletion.CASCADE, related_name="reads", to="comment.comment"
                    ),
                ),
                (
                    "reader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="read_comments", to="user.profile"
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("reader", "comment")},
            },
        ),
    ]
