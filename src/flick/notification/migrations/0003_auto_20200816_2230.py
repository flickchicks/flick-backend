# Generated by Django 3.0.6 on 2020-08-16 22:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("notification", "0002_notification_to_user")]

    operations = [
        migrations.RemoveField(model_name="notification", name="collaborator_added"),
        migrations.RemoveField(model_name="notification", name="collaborator_removed"),
    ]
