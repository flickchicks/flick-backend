# Generated by Django 3.0.6 on 2020-06-27 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("user", "0006_auto_20200627_2042"), ("lst", "0009_auto_20200627_2042")]

    operations = [
        migrations.AlterField(
            model_name="lst",
            name="collaborators",
            field=models.ManyToManyField(blank=True, related_name="collab_lsts", to="user.Profile"),
        ),
        migrations.AlterField(
            model_name="lst",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="owner_lsts", to="user.Profile"
            ),
        ),
    ]
