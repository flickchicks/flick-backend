from asset.models import AssetBundle
from django.contrib.auth.models import User
from django.db import models


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

    @property
    def total_likes(self):
        return Like.objects.filter(item_id=self.id).count()

    @property
    def likes(self):
        likes = []
        for like in Like.objects.filter(item_id=self.id):
            likes.append(like.owner.username)
        return likes

    @property
    def total_comments(self):
        return Comment.objects.filter(item_id=self.id).count()

    @property
    def comments(self):
        comments = []
        for comment in Comment.objects.filter(item_id=self.id):
            c = {}
            c["body"] = comment.body
            c["username"] = comment.owner.username
            c["created_at"] = comment.created_at
            comments.append(c)
        return comments


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

    class Meta:
        unique_together = ("item", "owner")
