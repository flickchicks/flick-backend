# Generated by Django 3.0.7 on 2020-09-05 18:34

from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("notification", "0001_initial"),
        ("user", "0001_initial"),
        ("lst", "0002_auto_20200905_1834"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="collaborators_added",
            field=models.ManyToManyField(blank=True, related_name="added_to_lst_notification", to="user.Profile"),
        ),
        migrations.AddField(
            model_name="notification",
            name="collaborators_removed",
            field=models.ManyToManyField(blank=True, related_name="removed_from_lst_notification", to="user.Profile"),
        ),
        migrations.AddField(
            model_name="notification",
            name="from_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_notification",
                to="user.Profile",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="lst",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notification",
                to="lst.Lst",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="new_owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="newly_owned_lst_notification",
                to="user.Profile",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="to_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_notification",
                to="user.Profile",
            ),
        ),
    ]
