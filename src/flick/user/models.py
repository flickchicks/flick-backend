from asset.models import AssetBundle
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


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
    social_id = models.TextField(blank=True, null=True)
    social_id_token_type = models.TextField(blank=True, null=True)
    social_id_token = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}, {self.user.first_name}"

    @property
    def num_notifs(self):
        from notification.models import Notification
        from suggestion.models import PrivateSuggestion

        return (
            Notification.objects.filter(
                Q(to_user=self) & ~(Q(notif_type="friend_request") & Q(friend_request_accepted=False))
            ).count()
            + PrivateSuggestion.objects.filter(to_user=self.user).count()
        )

    def upload_profile_pic(self):
        from upload.utils import upload_image

        if self.profile_pic:
            asset_bundle = upload_image(self.profile_pic, self.user)
            if not asset_bundle or not isinstance(asset_bundle, AssetBundle):
                print("Could not upload profile pic")
            self.profile_asset_bundle = asset_bundle
            self.profile_pic = None

    def save(self, *args, **kwargs):
        try:
            self.upload_profile_pic()
        except Exception as e:
            # catch the error so we prevent it from blocking registration
            print(f"Error creating profile: {e}")
        super(Profile, self).save(*args, **kwargs)
