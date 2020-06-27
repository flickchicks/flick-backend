from django.contrib.auth.models import User
from django.db import models

from asset.models import AssetBundle

# from lst.models import Lst


class Profile(models.Model):
    """
    User profile model. Matches one to one with built-in Django user model.
    """

    ROLE_CHOICES = (("consumer", "Consumer"), ("staff", "Staff"))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default="consumer")
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.TextField(blank=True, null=True)
    profile_asset_bundle = models.ForeignKey(AssetBundle, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    social_id_token_type = models.TextField(blank=True, null=True)
    social_id_token = models.TextField(blank=True, null=True)
    # owner_lsts = models.ManyToManyField(Lst, related_name="owner_lsts", blank=True)
    # collab_lsts = models.ManyToManyField(Lst, related_name="collab_lsts", blank=True)

    def __str__(self):
        return f"{self.user.username}, {self.user.first_name}"

    def upload_profile_pic(self):
        from upload.utils import upload_image

        if self.profile_pic:
            asset_bundle = upload_image(self.profile_pic, self.user)
            if not asset_bundle:
                print("Could not upload profile pic")
            elif not isinstance(asset_bundle, AssetBundle):
                print(asset_bundle)

            self.profile_asset_bundle = asset_bundle
            self.profile_pic = None

    def save(self, *args, **kwargs):
        self.upload_profile_pic()
        super(Profile, self).save(*args, **kwargs)
