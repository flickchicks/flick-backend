# Generated by Django 3.0.6 on 2021-02-20 22:07

from django.conf import settings
from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("discover", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("discover_recommend", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="discover",
            name="list_recommendations",
            field=models.ManyToManyField(
                blank=True, related_name="list_recommend", to="discover_recommend.DiscoverRecommendation"
            ),
        ),
        migrations.AddField(
            model_name="discover",
            name="show_recommendations",
            field=models.ManyToManyField(
                blank=True, related_name="show_recommend", to="discover_recommend.DiscoverRecommendation"
            ),
        ),
        migrations.AddField(
            model_name="discover",
            name="user",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
