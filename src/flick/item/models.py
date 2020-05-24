from django.db import models

from django.contrib.auth.models import User

from asset.models import AssetBundle

# Create your models here.
class Item(models.Model):
    """
    A 'post' that can have a photo, comments, likes, and owner.
    """
    asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Item: {self.owner}: {self.asset_bundle}"

class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Like(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
