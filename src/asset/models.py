from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class AssetBundle(models.Model):
    """
    Deal with all types of images: thumbnails, regular size, etc.
    {base_url}{ab_kind}/{ab_salt}_{a_kind}.{a_extension}
    ab_salt = asset bundle salt
    a_kind = asset kind
    """

    KIND_CHOICES = (
        ("image", "Image"),  # image shown in admin, Image shown in database
        ("video", "Video"),
    )
    salt = models.CharField(max_length=16)  # unique id, used to generate file names
    kind = models.CharField(max_length=5, choices=KIND_CHOICES, default="image")
    base_url = models.CharField(max_length=255, default=settings.S3_BASE_URL)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AssetBundle: {self.salt}"

    @property
    def asset_urls(self):
        assets = Asset.objects.filter(asset_bundle=self)
        urls = {}
        for a in assets:
            urls[a.kind] = a.full_url
        return urls


class Asset(models.Model):
    KIND_CHOICES = (("original", "Original"), ("large", "Large"), ("small", "Small"))

    EXTENSION_CHOICES = (
        ("png", "png"),
        ("gif", "gif"),
        ("jpg", "jpg"),
        ("jpeg", "jpeg"),
    )
    asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE)
    kind = models.CharField(max_length=8, choices=KIND_CHOICES, default=settings.S3_BASE_URL)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    extension = models.CharField(max_length=4, choices=EXTENSION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processing = models.BooleanField()

    def __str__(self):
        return f"Asset: {self.asset_bundle.salt}: {self.kind}"

    @property
    def full_url(self):
        return f"{self.asset_bundle.base_url}{self.asset_bundle.kind}/{self.asset_bundle.salt}_{self.kind}.{self.extension}"
