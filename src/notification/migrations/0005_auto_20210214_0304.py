# Generated by Django 3.1.5 on 2021-02-14 03:04

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("group", "0002_group_votes"),
        ("notification", "0004_auto_20210129_2248"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notification",
                to="group.group",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="notif_type",
            field=models.CharField(
                choices=[
                    ("list_invite", "List Invite"),
                    ("list_edit", "List Edit"),
                    ("incoming_friend_request_accepted", "Incoming Friend Request Accepted"),
                    ("outgoing_friend_request_accepted", "Outoing Friend Request Accepted"),
                    ("comment_like", "Comment Like"),
                    ("list_like", "List Like"),
                    ("group_invite", "Group Invite"),
                ],
                default=None,
                max_length=50,
            ),
        ),
    ]
