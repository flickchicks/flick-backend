from django.db import models

from django.contrib.auth.models import User

from asset.models import AssetBundle

# Create your models here.
class Item(models.Model):
    """
    A 'post' that can have a photo, comments, likes, and owner.
    """
    # title = models.CharField(max_length=255)
    # subtitle = models.CharField(max_length=255, blank=True, null=True)
    # like_count = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE)


    def __unicode__(self):
        return self.title

class Comment(models.Model):
    pass

class Like(models.Model):
    pass 