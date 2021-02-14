# Generated by Django 3.0.6 on 2021-01-20 19:43

from django.conf import settings
from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AssetBundle",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("salt", models.CharField(max_length=16)),
                (
                    "kind",
                    models.CharField(choices=[("image", "Image"), ("video", "Video")], default="image", max_length=5),
                ),
                ("base_url", models.CharField(default="https://flick.s3-us-west-1.amazonaws.com/", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "kind",
                    models.CharField(
                        choices=[("original", "Original"), ("large", "Large"), ("small", "Small")],
                        default="https://flick.s3-us-west-1.amazonaws.com/",
                        max_length=8,
                    ),
                ),
                ("width", models.IntegerField(default=0)),
                ("height", models.IntegerField(default=0)),
                (
                    "extension",
                    models.CharField(
                        choices=[("png", "png"), ("gif", "gif"), ("jpg", "jpg"), ("jpeg", "jpeg")], max_length=4
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_processing", models.BooleanField()),
                (
                    "asset_bundle",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="asset.AssetBundle"),
                ),
            ],
        ),
    ]