# Generated by Django 3.1.5 on 2021-03-06 02:43

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("lst", "0001_initial"),
        ("group", "0001_initial"),
        ("comment", "0001_initial"),
        ("suggestion", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "notif_type",
                    models.CharField(
                        choices=[
                            ("list_invite", "List Invite"),
                            ("list_edit", "List Edit"),
                            ("incoming_friend_request_accepted", "Incoming Friend Request Accepted"),
                            ("outgoing_friend_request_accepted", "Outoing Friend Request Accepted"),
                            ("comment_like", "Comment Like"),
                            ("list_like", "List Like"),
                            ("suggestion_like", "Suggestion Like"),
                            ("group_invite", "Group Invite"),
                        ],
                        default=None,
                        max_length=50,
                    ),
                ),
                ("num_shows_added", models.IntegerField(blank=True, null=True)),
                ("num_shows_removed", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "collaborators_added",
                    models.ManyToManyField(blank=True, related_name="added_to_lst_notification", to="user.Profile"),
                ),
                (
                    "collaborators_removed",
                    models.ManyToManyField(blank=True, related_name="removed_from_lst_notification", to="user.Profile"),
                ),
                (
                    "comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification",
                        to="comment.comment",
                    ),
                ),
                (
                    "from_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_notification",
                        to="user.profile",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification",
                        to="group.group",
                    ),
                ),
                (
                    "lst",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification",
                        to="lst.lst",
                    ),
                ),
                (
                    "new_owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="newly_owned_lst_notification",
                        to="user.profile",
                    ),
                ),
                (
                    "suggestion",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification",
                        to="suggestion.privatesuggestion",
                    ),
                ),
                (
                    "to_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_notification",
                        to="user.profile",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
