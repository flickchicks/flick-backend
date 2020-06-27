# Generated by Django 3.0.6 on 2020-05-31 01:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("show", "0003_auto_20200531_0040"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lst", "0002_auto_20200531_0052"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lst",
            name="collaborators",
            field=models.ManyToManyField(blank=True, related_name="collaborators", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(model_name="lst", name="shows", field=models.ManyToManyField(blank=True, to="show.Show")),
    ]
