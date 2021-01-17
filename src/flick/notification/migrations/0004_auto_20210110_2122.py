# Generated by Django 3.0.6 on 2021-01-10 21:22

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0003_remove_notification_has_viewed"),
    ]

    operations = [
        migrations.AddField(model_name="notification", name="updated_at", field=models.DateTimeField(auto_now=True),),
        migrations.AlterField(
            model_name="notification",
            name="notif_type",
            field=models.CharField(
                choices=[
                    ("list_invite", "List Invite"),
                    ("list_edit", "List Edit"),
                    ("friend_request", "Friend Request"),
                    ("accepted_request", "Accepted Request"),
                ],
                default=None,
                max_length=20,
            ),
        ),
    ]