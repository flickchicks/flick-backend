from asset.models import AssetBundle
from django.contrib.auth.models import User
from django.db import models

from lst.models import Lst


# Create your models here.
class Profile(models.Model):
    """
    User profile model. Matches one to one with built-in Django user model.
    """

    ROLE_CHOICES = (("consumer", "Consumer"), ("staff", "Staff"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default="consumer")
    bio = models.TextField(blank=True, null=True)
    profile_asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE, blank=True, null=True)
    profile_pic = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    social_id_token_type = models.TextField(blank=True, null=True)
    social_id_token = models.TextField(blank=True, null=True)
    owner_lsts = models.ManyToManyField(Lst, related_name="owner_lsts", blank=True)
    collab_lsts = models.ManyToManyField(Lst, related_name="collab_lsts", blank=True)
    # owner_lsts = models.ForeignKey(Lst, related_name='owner_lsts', on_delete=models.CASCADE)
    # collab_lsts = models.ForeignKey(Lst, related_name='collab_lsts', on_delete=models.CASCADE)

    # override what django admin displays
    def __str__(self):
        return f"{self.user.username}, {self.user.name}"
