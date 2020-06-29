# Generated by Django 3.0.6 on 2020-06-21 23:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("lst", "0003_auto_20200531_0103")]

    operations = [
        migrations.RemoveField(model_name="lst", name="collaborators"),
        migrations.AddField(
            model_name="lst",
            name="collaborator",
            field=models.ManyToManyField(blank=True, related_name="collaborator", to=settings.AUTH_USER_MODEL),
        ),
    ]